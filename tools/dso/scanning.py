"""Repository scanning through manifest plugins; standard library only."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone

import manifest
from reports import (SCHEMA_VERSION, SEVERITIES, deduplicate, digest, gate,  # noqa: F401 (CLI and MCP API)
                     selected_plugins, validate_report)
from runtime import ScanError, Cancelled, run_process, snapshot, check_cancel, loads, text, EXCLUDED

ROOT = manifest.ROOT
DEFAULT_PROFILE = 'ci-blocking'
CORE = [Path(__file__).with_name(n) for n in ('scanning.py', 'runtime.py', 'reports.py', 'manifest.py', 'plugins.json')]
VERSION = re.compile(r'(?<![0-9])[0-9]+\.[0-9]+\.[0-9]+(?![0-9])')


def executable_path(name):
    search = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get('PATH', '')])
    return shutil.which(name, path=search)


def detected_version(executable, spec, cwd, timeout, cancel=None):
    rc, out = run_process([executable, *spec['version_args']], cwd, timeout, cancel)
    match = VERSION.search(out)
    return match.group() if rc == 0 and match else None


def doctor(engine='native', cancel=None):
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
        except (OSError, ValueError):
            return {'engine': engine, 'ready': False, 'daemon_version': None, 'tools': [],
                    'error': 'Docker daemon unavailable; check installation and context'}
    tools = {}
    for name, spec in sorted(manifest.plugins().items()):
        tools.setdefault(spec['tool'], (spec, []))[1].append(name)
    for tool, (spec, plugins) in sorted(tools.items()):
        check_cancel(cancel)
        executable = executable_path(tool) if engine == 'native' else docker
        record = {'tool': tool, 'plugins': plugins, 'ready': False, 'expected_version': spec['version'],
                  'detected_version': None, 'executable': executable, 'image': spec['image'] if engine == 'docker' else None}
        try:
            if not executable:
                raise ScanError('missing_executable', 'Scanner executable unavailable')
            if engine == 'docker':
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
    return {'engine': engine, 'ready': all(r['ready'] for r in results),
            'daemon_version': daemon, 'tools': results}


def normalize(plugin, data, source):
    """Allowlist fields; never copy scanner snippets, messages, matches or secrets."""
    return deduplicate(manifest.adapter(plugin).parse(data, plugin, Path(source)))


def policy_digest(profile, names):
    selection = manifest.profile(profile)['plugins']
    paths = set(CORE)
    for name in names:
        adapter = manifest.adapter(name)
        paths.add(Path(adapter.__file__))
        paths.update(adapter.policy_files(selection[name], ROOT))
    return digest([profile] + [(str(p.relative_to(ROOT)), hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(paths)])


def cache_dir(work):
    """Reuse DSO_CACHE_DIR when this UID can write it (e.g. image volume); otherwise a private cache."""
    shared = os.environ.get('DSO_CACHE_DIR')
    if shared and Path(shared).is_dir() and os.access(shared, os.W_OK | os.X_OK):
        return shared
    return str(work / 'cache')


class Context:
    """What an adapter may use: trusted options and the paths its scanner sees."""

    def __init__(self, plugin, options, engine, work, source):
        self.plugin, self.spec, self.options, self.root = plugin, manifest.plugin(plugin), options, ROOT
        self.source_host = source
        self.config_host = work / 'config' / plugin
        self.config_host.mkdir(mode=0o700)
        inside = engine == 'docker'
        self.source = '/src' if inside else str(source)
        self.config = f'/work/config/{plugin}' if inside else str(self.config_host)
        self.output = ('/work' if inside else str(work)) + '/result.json'
        self.cache = '/work/cache' if inside else cache_dir(work)


def scan_repo(path, tools=None, engine='native', timeout=300, project=None, cancel=None, exclusions=(), profile=DEFAULT_PROFILE):
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
              'input': {'files': 0, 'bytes': 0, 'sha256': '0' * 64},
              'complete': True, 'runs': [], 'findings': []}
    with tempfile.TemporaryDirectory(prefix='dso-') as directory:
        work = Path(directory)
        source_path = work / 'source'
        try:
            report['input'] = snapshot(target, source_path, cancel, exclusions)
        except ScanError as exc:
            report['complete'] = False
            report['runs'] = [{'plugin': n, 'status': 'error', 'finding_count': 0, 'exit_code': None,
                               'error_code': exc.code, 'error': str(exc)} for n in names]
            return report
        (work / 'config').mkdir(mode=0o700)
        contexts = {}
        for name in names:
            # Trusted kit configuration only; a broken kit raises instead of scanning less.
            contexts[name] = Context(name, selection['plugins'][name], engine, work, source_path)
            manifest.adapter(name).prepare(contexts[name])
        token = os.urandom(24).hex()
        (source_path / '.dso-sentinel').write_text(token)
        (work / 'sentinel').write_text(token)
        docker = executable_path('docker') if engine == 'docker' else None
        for name in names:
            check_cancel(cancel)
            ctx, adapter, spec = contexts[name], manifest.adapter(name), manifest.plugin(name)
            run = {'plugin': name, 'status': 'error', 'finding_count': 0, 'exit_code': None}
            container_name = 'dso-' + os.urandom(12).hex()
            try:
                executable = executable_path(spec['tool']) if engine == 'native' else docker
                if not executable:
                    raise ScanError('missing_executable', 'Scanner executable unavailable')
                if hasattr(adapter, 'preflight'):
                    adapter.preflight(ctx)
                if engine == 'native' and detected_version(executable, spec, work, min(timeout, 15), cancel) != spec['version']:
                    raise ScanError('version', 'Scanner version differs from reviewed version ' + spec['version'])
                args = [executable, *adapter.command(ctx)]
                if engine == 'docker':
                    for mount in (source_path, work):
                        if ',' in str(mount):
                            raise ScanError('mount', 'Docker mount path contains a comma; choose a different TMPDIR')
                    prefix = [docker, 'run', '--rm', '--name', container_name, '--read-only',
                              '--cap-drop=ALL', '--security-opt=no-new-privileges', '--pids-limit', '256',
                              '--memory', '3g', '--user', f'{os.getuid()}:{os.getgid()}',
                              '--tmpfs', '/tmp:rw,nosuid,nodev,size=256m', '-e', 'HOME=/tmp',
                              '--mount', f'type=bind,src={source_path},dst=/src,readonly',
                              '--mount', f'type=bind,src={work},dst=/work', '-w', '/work']
                    if not spec['network']:
                        prefix += ['--network', 'none']
                    else:
                        for key in ('HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy'):
                            if key in os.environ:
                                prefix += ['-e', key]
                        ca = os.environ.get('SSL_CERT_FILE')
                        if ca:
                            ca_path = Path(ca).resolve(strict=True)
                            shutil.copyfile(ca_path, work / 'ca.pem')
                            prefix += ['-e', 'SSL_CERT_FILE=/work/ca.pem']
                    probe = ['--entrypoint', '/bin/sh', spec['image'], '-c',
                             'test "$(cat /work/sentinel)" = "$1" && test "$(cat /src/.dso-sentinel)" = "$1"', 'sh', token]
                    rc, _ = run_process(prefix + probe, work, timeout, cancel)
                    if rc:
                        raise ScanError('mount_visibility', 'Docker cannot read the private snapshot; daemon and client need identical shared TMPDIR paths')
                    args = prefix + [spec['image'], *spec['image_command'], *adapter.command(ctx)]
                (work / 'result.json').unlink(missing_ok=True)
                code, _ = run_process(args, work, timeout, cancel)
                run['exit_code'] = code
                codes = spec['exit_codes']
                if code not in (codes['clean'], codes['findings']):
                    raise ScanError('execution', 'Scanner failed; exit code is recorded separately')
                try:
                    with (work / 'result.json').open('rb') as stream:
                        data = loads(stream.read(20 * 1024 * 1024 + 1))
                    records = normalize(name, data, ctx.source)
                except (OSError, ValueError, KeyError, TypeError, AttributeError):
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
    report['findings'].sort(key=lambda f: f['id'])
    return report


def prepare_output(path):
    path = Path(path)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('Output must be a regular file, not a symlink or device')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryFile(dir=path.parent):
        pass


def write_report(path, report):
    """Atomic private output; replacement does not follow an existing symlink."""
    path = Path(path)
    prepare_output(path)
    descriptor, temporary = tempfile.mkstemp(prefix='.dso-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
