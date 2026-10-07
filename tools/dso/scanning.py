"""Repository scanning through manifest plugins; standard library only."""
from __future__ import annotations

import hashlib
from contextlib import ExitStack
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

import config
import inventory
import manifest
from reports import (IMAGE_REFERENCE, SCHEMA_VERSION, SEVERITIES, deduplicate, digest, gaps, gate, issues,  # noqa: F401
                     check_shape, selected_plugins, validate_report, waive)
import runtime
from runtime import ScanError, Cancelled, run_process, snapshot, check_cancel, loads, text, EXCLUDED

ROOT = manifest.ROOT
VERSION = '0.3.0'
DEFAULT_PROFILE = 'ci-blocking'
DEFAULT_IMAGE_PROFILE = 'image'
CORE = [Path(__file__).with_name(n) for n in ('scanning.py', 'runtime.py', 'reports.py', 'manifest.py', 'inventory.py',
                                              'register.py', 'plugins.json')]
VERSION_NUMBER = re.compile(r'(?<![0-9])[0-9]+\.[0-9]+\.[0-9]+(?![0-9])')


def executable_path(name):
    search = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get('PATH', '')])
    return shutil.which(name, path=search)


def detected_version(executable, spec, cwd, timeout, cancel=None):
    rc, out = run_process([executable, *spec['version_args']], cwd, timeout, cancel)
    match = VERSION_NUMBER.search(out)
    return match.group() if rc == 0 and match else None


def doctor(engine='native', cancel=None, profile=DEFAULT_PROFILE):
    if engine not in ('native', 'docker'):
        raise ValueError('engine must be native or docker')
    results = []
    daemon = None
    docker = executable_path('docker')
    if engine == 'docker':
        try:
            if not docker:
                raise ScanError('missing_executable', 'Docker executable unavailable')
            rc, daemon = run_process([docker, 'info', '--format', '{{.ServerVersion}}'], tempfile.gettempdir(), 15, cancel)
            if rc:
                raise ScanError('daemon', 'Docker daemon unavailable')
            daemon = daemon.strip()
        except Cancelled:
            raise
        except (OSError, ValueError):
            return {'engine': engine, 'ready': False, 'daemon_version': None, 'tools': [],
                    'error': 'Docker daemon unavailable; check installation and context'}
    tools = {}
    for name in sorted(manifest.profile(profile)['plugins']):
        spec = manifest.plugin(name)
        tools.setdefault(spec['tool'], (spec, []))[1].append(name)
    for tool, (spec, plugins) in sorted(tools.items()):
        check_cancel(cancel)
        executable = executable_path(spec['executable']) if engine == 'native' else docker
        record = {'tool': tool, 'plugins': plugins, 'ready': False, 'expected_version': spec['version'],
                  'detected_version': None, 'executable': executable, 'image': spec['image'] if engine == 'docker' else None}
        try:
            if not executable:
                raise ScanError('missing_executable', 'Scanner executable unavailable')
            if engine == 'docker' and spec['image'] is None:
                record['error'] = 'No reviewed image; this plugin runs only with --engine native'
            elif engine == 'docker':
                # No implicit pulls in doctor. Report actual local image readiness.
                rc, out = run_process([docker, 'image', 'inspect', spec['image'], '--format', '{{.Id}}'], tempfile.gettempdir(), 15, cancel)
                record['ready'] = rc == 0 and out.strip().startswith('sha256:')
                record['error'] = None if record['ready'] else 'Pinned image missing locally; scan may pull it'
            else:
                record['detected_version'] = detected_version(executable, spec, tempfile.gettempdir(), 15, cancel)
                record['ready'] = record['detected_version'] == spec['version']
                record['error'] = None if record['ready'] else 'Expected scanner version was not detected'
        except Cancelled:
            raise
        except (OSError, ValueError):
            record['error'] = 'Scanner unavailable or version check failed'
        results.append(record)
    root = cache_root()
    return {'engine': engine, 'profile': profile, 'ready': all(r['ready'] for r in results),
            'daemon_version': daemon, 'tools': results, 'cache': str(root) if root else None,
            'databases': database_status(manifest.profile(profile)['plugins'], engine)}


def normalize(plugin, data, source):
    """Allowlist fields; never copy scanner snippets, messages, matches or secrets."""
    records = manifest.adapter(plugin).parse(data, plugin, Path(source))
    for record in records:
        check_shape(record)
    return deduplicate(records)


def policy_digest(profile, names):
    selection = manifest.profile(profile)['plugins']
    paths = set(CORE)
    for name in names:
        adapter = manifest.adapter(name)
        paths.add(Path(adapter.__file__))
        paths.update(adapter.policy_files(selection[name], ROOT))
    return digest([profile] + [(str(p.relative_to(ROOT)), hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)])


def cache_root():
    """Where vulnerability databases persist: DSO_CACHE_DIR, else this user's private cache; None if neither is usable."""
    shared = config.load()[0]['cache_dir']
    if shared:
        path = Path(shared).resolve()
        if not path.is_dir() or not os.access(path, os.W_OK | os.X_OK):
            return None
        try:
            with tempfile.TemporaryFile(dir=path):
                pass
            return path
        except OSError:
            return None
    default = Path(os.environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'dso'
    try:
        default.mkdir(parents=True, exist_ok=True, mode=0o700)
        if default.is_symlink() or default.stat().st_uid != os.getuid() or default.stat().st_mode & 0o077:
            raise PermissionError()
        with tempfile.TemporaryFile(dir=default):
            pass
        return default
    except OSError:
        return None


def cache_dir(work):
    """Vulnerability databases are large, so native scans reuse the cache; otherwise the run directory."""
    root = cache_root()
    return str(root) if root else str(work / 'cache')


def disk_usage(path):
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob('*') if p.is_file() and not p.is_symlink())


def database_status(names, engine='native'):
    """Each vulnerability database the plugins need: reviewed sizes, and whether it is already cached."""
    root = cache_root()
    status = {}
    for name in names:
        database = manifest.plugin(name)['database']
        if database and database['path'] not in status:
            path = root / database['path'] if root else None
            present = bool(path and path.exists())
            status[database['path']] = dict(database, present=present, bytes=disk_usage(path) if present else 0,
                                            updated=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
                                            if present else None)
    return list(status.values())


class Context:
    """What an adapter may use: trusted options and the paths its scanner sees."""

    def __init__(self, plugin, options, engine, work, source, persistent_cache=None):
        self.plugin, self.spec, self.options, self.root = plugin, manifest.plugin(plugin), options, ROOT
        # A snapshot directory for repositories; the pinned reference itself for images.
        self.source_host = source if isinstance(source, Path) else None
        self.config_host = work / 'config' / plugin
        self.config_host.mkdir(mode=0o700)
        inside = engine == 'docker'
        self.source = ('/src' if inside else str(source)) if self.source_host else source
        self.config = f'/work/config/{plugin}' if inside else str(self.config_host)
        # A fresh directory per plugin: Docker Desktop's shared mounts can keep a stale entry for a
        # file another container wrote and the host deleted, which makes creating it fail (ENOENT).
        self.result_host = work / 'results' / plugin / 'result.json'
        self.result_host.parent.mkdir(mode=0o700)
        self.output = f'/work/results/{plugin}/result.json' if inside else str(self.result_host)
        self.cache = ('/cache' if persistent_cache else '/work/cache') if inside else str(persistent_cache or work / 'cache')


def tool_prefixes():
    """Environment prefixes of every manifest tool, so the caller's settings cannot change a scan."""
    return tuple(sorted({spec['tool'].upper().replace('-', '_') + '_' for spec in manifest.plugins().values()}))


def container(docker, name, source, work, network, cache=None):
    """docker run options shared by every plugin: read-only, unprivileged, only the snapshot and work mounted."""
    for mount in (source, work, cache):
        if mount is not None and ',' in str(mount):
            raise ScanError('mount', 'Docker mount path contains a comma; choose a different TMPDIR')
    prefix = [docker, 'run', '--rm', '--name', name, '--read-only',
              '--cap-drop=ALL', '--security-opt=no-new-privileges', '--pids-limit', '256',
              '--memory', '3g', '--user', f'{os.getuid()}:{os.getgid()}',
              # Some scanner images ship /tmp as root-only; explicitly allow the caller's UID.
              '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m,mode=1777', '-e', 'HOME=/tmp']
    if source is not None:
        prefix += ['--mount', f'type=bind,src={source},dst=/src,readonly']
    prefix += ['--mount', f'type=bind,src={work},dst=/work', '-w', '/work']
    if cache is not None:
        prefix += ['--mount', f'type=bind,src={cache},dst=/cache']
    if not network:
        return prefix + ['--network', 'none']
    for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'):
        if key in os.environ:
            prefix += ['-e', key]
    ca = os.environ.get('SSL_CERT_FILE')
    if ca:
        shutil.copyfile(Path(ca).resolve(strict=True), work / 'ca.pem')
        prefix += ['-e', 'SSL_CERT_FILE=/work/ca.pem']
    return prefix


def probe(docker, source, work, timeout, cancel=None, cache=None):
    """Check mount visibility without overwriting source files or leaving probe files for scanners."""
    token = os.urandom(24).hex()
    name = 'dso-' + os.urandom(12).hex()
    try:
        with ExitStack() as temporary:
            checks, arguments = [], [token]
            for directory, mount in ((work, '/work'), (source, '/src'), (cache, '/cache')):
                if directory is None:
                    continue
                sentinel = temporary.enter_context(tempfile.NamedTemporaryFile(
                    mode='w', prefix='.dso-probe-', dir=directory))
                sentinel.write(token)
                sentinel.flush()
                arguments.append(Path(sentinel.name).name)
                checks.append(f'test "$(cat "{mount}/${len(arguments)}")" = "$1"')
            args = container(docker, name, source, work, False, cache) + [
                '--entrypoint', '/bin/sh', manifest.probe_image(), '-c', ' && '.join(checks), 'sh', *arguments]
            code, _ = run_process(args, work, timeout, cancel)
    except Cancelled:
        raise
    except ScanError as exc:
        return exc
    except OSError:
        return ScanError('mount_visibility', 'Docker probe could not access the snapshot, cache or executable')
    finally:
        try:
            run_process([docker, 'rm', '-f', name], work, 15)
        except (OSError, ValueError):
            pass
    if code:
        return ScanError('mount_visibility', 'Docker cannot read the snapshot or cache; daemon and client need shared mount paths')
    return None


def run_plugins(report, names, selection, engine, work, source, timeout, cancel, notify):
    """Run each plugin the same way: prepare, version check, sandbox, timeout, parse and validate."""
    (work / 'config').mkdir(mode=0o700)
    (work / 'results').mkdir(mode=0o700)
    # Only plugins with a vulnerability database get the shared cache: scanners that parse the
    # target's files must not be able to rewrite the databases later scans trust.
    persistent_cache = cache_root()
    caches = {n: persistent_cache if manifest.plugin(n)['database'] else None for n in names}
    contexts = {}
    for name in names:
        # Trusted kit configuration only; a broken kit raises instead of scanning less.
        contexts[name] = Context(name, selection['plugins'][name], engine, work, source, caches[name])
        manifest.adapter(name).prepare(contexts[name])
    docker = executable_path('docker') if engine == 'docker' else None
    probe_error = probe(docker, source if isinstance(source, Path) else None, work, timeout, cancel,
                        persistent_cache if any(caches.values()) else None) if docker else None
    for name in names:
        check_cancel(cancel)
        ctx, adapter, spec = contexts[name], manifest.adapter(name), manifest.plugin(name)
        run = {'plugin': name, 'status': 'error', 'finding_count': 0, 'exit_code': None}
        notify('start', name)
        container_name = 'dso-' + os.urandom(12).hex()
        try:
            executable = executable_path(spec['executable']) if engine == 'native' else docker
            if not executable:
                raise ScanError('missing_executable', 'Scanner executable unavailable')
            if engine == 'docker' and spec['image'] is None:
                raise ScanError('no_image', 'No reviewed image for this plugin; scan with --engine native')
            if probe_error:
                raise probe_error
            if hasattr(adapter, 'preflight'):
                adapter.preflight(ctx)
            if engine == 'native' and detected_version(executable, spec, work, min(timeout, 15), cancel) != spec['version']:
                raise ScanError('version', 'Scanner version differs from reviewed version ' + spec['version'])
            extra = adapter.environment(ctx) if hasattr(adapter, 'environment') else {}
            args = [executable, *adapter.command(ctx)]
            if engine == 'docker':
                prefix = container(docker, container_name, source if isinstance(source, Path) else None, work,
                                   spec['network'], caches[name])
                for key, value in extra.items():
                    prefix += ['-e', f'{key}={value}']
                if spec['image_entrypoint']:
                    prefix += ['--entrypoint', spec['image_entrypoint']]
                args = prefix + [spec['image'], *spec['image_command'], *adapter.command(ctx)]
            result = ctx.result_host
            code, _ = run_process(args, work, timeout, cancel, extra_env=extra if engine == 'native' else None,
                                  output_path=result if getattr(adapter, 'OUTPUT', 'file') == 'stdout' else None,
                                  clear=tool_prefixes(), errors_on=getattr(adapter, 'ERRORS', ()))
            run['exit_code'] = code
            codes = spec['exit_codes']
            if code not in (codes['clean'], codes['findings']):
                raise ScanError('execution', 'Scanner failed; exit code is recorded separately')
            try:
                with result.open('rb') as stream:
                    raw = stream.read(runtime.REPORT_LIMIT + 1)
                if len(raw) > runtime.REPORT_LIMIT:
                    raise ScanError('report_limit', f'Scanner output exceeds {runtime.REPORT_LIMIT >> 20} MiB; {runtime.LIMIT_HINT}')
                data = ([loads(line) for line in raw.splitlines() if line.strip()]
                        if getattr(adapter, 'FORMAT', 'json') == 'jsonl' else loads(raw, runtime.REPORT_LIMIT))
                records = normalize(name, data, ctx.source)
                if len(report['findings']) + len(records) > runtime.MAX_FINDINGS:
                    raise ScanError('report_limit', f'Scan exceeds {runtime.MAX_FINDINGS} findings; raise max_findings in dso config or pass --max-findings')
            except ScanError:
                raise
            except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError):
                raise ScanError('report', 'Scanner report is missing, invalid or incomplete') from None
            if codes['findings'] != codes['clean'] and bool(records) != (code == codes['findings']):
                raise ScanError('report', 'Scanner exit status disagrees with its report')
            report['findings'].extend(records)
            run.update(status='complete', finding_count=len(records))
        except Cancelled:
            raise
        except ScanError as exc:
            run.update(error_code=exc.code, error=str(exc))
            report['complete'] = False
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            run.update(error_code='execution', error='Scanner could not execute with the reviewed configuration')
            report['complete'] = False
        finally:
            if engine == 'docker' and docker:
                try:
                    run_process([docker, 'rm', '-f', container_name], work, 15)
                except (OSError, ValueError):
                    pass
        report['runs'].append(run)
        notify('done', name, run)


def scan_repo(path, tools=None, engine='native', timeout=300, project=None, cancel=None, exclusions=(),
              profile=DEFAULT_PROFILE, progress=None, origin=None):
    """progress(event, step, detail) is called with 'start' and 'done' for the snapshot and each plugin.
    origin records where a fetched tree came from: {'url': ..., 'commit': ...}."""
    def notify(event, step, detail=None):
        if progress is not None:
            progress(event, step, detail)
    selection = manifest.profile(profile)
    if selection['target'] != 'repo':
        raise ValueError('Profile does not scan repositories')
    names = selected_plugins(tools, profile)
    text(str(path), 'target', 4096)
    text(project, 'project', 200)
    if engine not in ('native', 'docker') or type(timeout) is not int or not 1 <= timeout <= 1800:
        raise ValueError('Invalid engine or timeout (1–1800 seconds per scanner)')
    target = Path(path).resolve(strict=True)
    report = {'schema_version': SCHEMA_VERSION, 'project': project, 'target': {'type': 'repo'},
              'created_at': datetime.now(timezone.utc).isoformat(),
              'coverage': {'profile': profile, 'plugins': names,
                           'versions': {n: manifest.plugin(n)['version'] for n in names},
                           'engine': engine, 'policy_digest': policy_digest(profile, names),
                           'exclusions': sorted(set(exclusions)), 'default_exclusions': sorted(EXCLUDED)},
              'input': {'files': 0, 'bytes': 0, 'sha256': '0' * 64, **({'origin': dict(origin)} if origin else {})},
              'complete': True, 'runs': [], 'findings': []}
    with tempfile.TemporaryDirectory(prefix='dso-') as directory:
        work = Path(directory)
        source_path = work / 'source'
        notify('start', 'snapshot')
        try:
            report['input'] = snapshot(target, source_path, cancel, exclusions)
            if origin is not None:
                report['input']['origin'] = dict(origin)
            report['input']['inventory'] = inventory.collect(source_path)
        except ScanError as exc:
            report['complete'] = False
            report['runs'] = [{'plugin': n, 'status': 'error', 'finding_count': 0, 'exit_code': None,
                               'error_code': exc.code, 'error': str(exc)} for n in names]
            notify('done', 'snapshot', {'status': 'error', 'error_code': exc.code, 'error': str(exc)})
            return report
        notify('done', 'snapshot', dict(report['input'], status='complete'))
        run_plugins(report, names, selection, engine, work, source_path, timeout, cancel, notify)
    report['findings'].sort(key=lambda f: f['id'])
    return report


def scan_image(reference, tools=None, engine='native', timeout=300, project=None, cancel=None,
               profile=DEFAULT_IMAGE_PROFILE, progress=None):
    """Scan a container image pinned by digest; scanners pull it from its registry without credentials."""
    def notify(event, step, detail=None):
        if progress is not None:
            progress(event, step, detail)
    selection = manifest.profile(profile)
    if selection['target'] != 'image':
        raise ValueError('Profile does not scan container images')
    names = selected_plugins(tools, profile)
    if not isinstance(reference, str) or not IMAGE_REFERENCE.fullmatch(reference):
        raise ValueError('Give an image pinned by digest, such as registry/name:tag@sha256:<64 hex>')
    text(project, 'project', 200)
    if engine not in ('native', 'docker') or type(timeout) is not int or not 1 <= timeout <= 1800:
        raise ValueError('Invalid engine or timeout (1–1800 seconds per scanner)')
    report = {'schema_version': SCHEMA_VERSION, 'project': project, 'target': {'type': 'image'},
              'created_at': datetime.now(timezone.utc).isoformat(),
              'coverage': {'profile': profile, 'plugins': names,
                           'versions': {n: manifest.plugin(n)['version'] for n in names},
                           'engine': engine, 'policy_digest': policy_digest(profile, names),
                           'exclusions': [], 'default_exclusions': []},
              'input': {'reference': reference}, 'complete': True, 'runs': [], 'findings': []}
    with tempfile.TemporaryDirectory(prefix='dso-') as directory:
        run_plugins(report, names, selection, engine, Path(directory), reference, timeout, cancel, notify)
    report['findings'].sort(key=lambda f: f['id'])
    return report


def preferred_profile(target):
    """The most thorough profile for a target whose scanners are all installed; the default otherwise."""
    candidates = sorted(((len(spec['plugins']), name) for name, spec in manifest.profiles().items() if spec['target'] == target),
                        reverse=True)
    for _, name in candidates:
        if all(executable_path(manifest.plugin(plugin)['executable']) for plugin in manifest.profile(name)['plugins']):
            return name
    return DEFAULT_IMAGE_PROFILE if target == 'image' else DEFAULT_PROFILE


def image_project(reference):
    """The image name without tag or digest: findings of rebuilt images stay comparable."""
    name = reference.split('@', 1)[0]
    return name.rsplit(':', 1)[0] if ':' in name.rsplit('/', 1)[-1] else name


def prepare_output(path):
    path = Path(path)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('Output must be a regular file, not a symlink or device')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryFile(dir=path.parent):
        pass


def write_report(path, report):
    """Atomic private output that can be read back within DSO's JSON limit."""
    path = Path(path)
    prepare_output(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.dso-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            size = 1  # final newline counts toward the input limit too
            for chunk in json.JSONEncoder(indent=2, allow_nan=False).iterencode(report):
                encoded = chunk.encode('utf-8')
                size += len(encoded)
                if size > runtime.REPORT_LIMIT:
                    raise ScanError('report_limit', f'DSO report exceeds {runtime.REPORT_LIMIT >> 20} MiB; {runtime.LIMIT_HINT}')
                stream.write(encoded)
            stream.write(b'\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
