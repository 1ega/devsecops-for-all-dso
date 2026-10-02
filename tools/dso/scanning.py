"""Repository scanning and conservative delta gates; standard library only."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from runtime import (ScanError, Cancelled, run_process, snapshot, check_python, check_cancel,
                     read_json, loads, text, EXCLUDED)

PROFILE = "repo-v2:snapshot,python3-starter,offline-dependencies"

ROOT = Path(__file__).resolve().parents[2]
TOOLS = {
    'gitleaks': ('8.30.1', 'ghcr.io/gitleaks/gitleaks:v8.30.1@sha256:c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f'),
    'semgrep': ('1.179.0', 'semgrep/semgrep:1.179.0@sha256:93963d9295a366f59e4850127b1550400ee7b388f04fe144e4a1f6325d96e01b'),
    'trivy': ('0.75.0', 'aquasec/trivy:0.75.0@sha256:af6acf9a6b85dfe389a1941505c0ce9efef52a4719635e1a962f022a3d855daa'),
}
SEVERITIES = {'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4, 'unknown': -1}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def selected_tools(names):
    names = list(TOOLS) if names is None else names
    if not isinstance(names, list) or not names or any(not isinstance(n, str) or n not in TOOLS for n in names):
        raise ValueError('Select one or more of: ' + ', '.join(TOOLS))
    if len(names) != len(set(names)):
        raise ValueError('Duplicate scanner selection')
    return sorted(names)


def executable_path(name):
    search = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get('PATH', '')])
    return shutil.which(name, path=search)


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
    for name, (expected, image) in TOOLS.items():
        check_cancel(cancel)
        executable = executable_path(name) if engine == 'native' else docker
        record = {'tool': name, 'ready': False, 'expected_version': expected,
                  'detected_version': None, 'executable': executable, 'image': image if engine == 'docker' else None}
        try:
            if not executable:
                raise ScanError('missing_executable', 'Scanner executable unavailable')
            if engine == 'docker':
                # No implicit pulls in doctor. Report actual local image readiness.
                rc, out = run_process([docker, 'image', 'inspect', image, '--format', '{{.Id}}'], tempfile.gettempdir(), 15, cancel)
                record['ready'] = rc == 0 and out.strip().startswith('sha256:')
                record['error'] = None if record['ready'] else 'Pinned image missing locally; scan may pull it'
            else:
                rc, out = run_process([executable, 'version' if name == 'gitleaks' else '--version'], tempfile.gettempdir(), 15, cancel)
                match = re.search(r'(?<![0-9])[0-9]+\.[0-9]+\.[0-9]+(?![0-9])', out)
                record['detected_version'] = match.group() if match else None
                record['ready'] = rc == 0 and record['detected_version'] == expected
                record['error'] = None if record['ready'] else 'Expected scanner version was not detected'
        except Cancelled:
            raise
        except (OSError, ValueError):
            record['error'] = 'Scanner unavailable or version check failed'
        results.append(record)
    return {'engine': engine, 'ready': all(r['ready'] for r in results),
            'daemon_version': daemon, 'tools': results}


def relative_path(value, target):
    text(value, 'finding path', 4096)
    path = Path(value)
    if path.is_absolute():
        try:
            path = path.relative_to(target)
        except ValueError:
            raise ValueError('Finding path outside scan target') from None
    if '..' in path.parts or path.as_posix() in ('.', ''):
        raise ValueError('Finding path escapes scan target')
    return path.as_posix()


def finding(tool, rule, path, severity, line=0, package='', version='', fixed='', fingerprint=''):
    text(rule, 'rule', 512)
    text(path, 'path', 4096)
    if type(line) is not int or line < 0:
        raise ValueError('Invalid finding line')
    for value in (package, version, fixed):
        text(value, 'package metadata', 2048, empty=True)
    if fingerprint and not re.fullmatch('[a-f0-9]{64}', fingerprint):
        raise ValueError('Invalid finding fingerprint')
    severity = str(severity).lower()
    if severity not in SEVERITIES:
        severity = 'unknown'
    record = {'tool': tool, 'rule_id': rule, 'path': path, 'line': line,
              'package': package, 'installed_version': version, 'fixed_version': fixed,
              'severity': severity, 'fingerprint': fingerprint}
    record['id'] = digest([tool, rule, path, line, package, version, fingerprint])
    return record


def normalize(tool, data, target):
    """Allowlist fields; never copy scanner snippets, messages, matches or secrets."""
    records = []
    if tool == 'gitleaks':
        if not isinstance(data, list):
            raise ValueError('Gitleaks report must be an array')
        for item in data:
            # Multi-line secrets (PEM keys) are valid; only the domain-separated hash is kept.
            secret = item['Secret']
            if not isinstance(secret, str) or not secret or len(secret) > 1024 * 1024:
                raise ValueError('Invalid secret match')
            fingerprint = hashlib.sha256(b'dso-secret-v2\0' + item['RuleID'].encode() + b'\0' + secret.encode()).hexdigest()
            records.append(finding(tool, item['RuleID'], relative_path(item['File'], target),
                                   'high', item['StartLine'], fingerprint=fingerprint))
    elif tool == 'semgrep':
        if not isinstance(data, dict) or not isinstance(data.get('results'), list) or not isinstance(data.get('errors'), list):
            raise ValueError('Invalid Semgrep report')
        if data['errors']:
            raise ValueError('Semgrep reported incomplete analysis')
        for item in data['results']:
            severity = {'ERROR': 'high', 'WARNING': 'medium', 'INFO': 'info',
                        'CRITICAL': 'critical', 'HIGH': 'high', 'MEDIUM': 'medium', 'LOW': 'low'}.get(item['extra']['severity'], 'unknown')
            records.append(finding(tool, item['check_id'], relative_path(item['path'], target),
                                   severity, item['start']['line']))
    elif tool == 'trivy':
        if not isinstance(data, dict) or data.get('SchemaVersion') != 2 or not isinstance((data.get('Results') or []), list) or not data.get('ArtifactName'):
            raise ValueError('Invalid Trivy report')
        for result in (data.get('Results') or []):
            path = relative_path(result['Target'], target)
            for item in result.get('Vulnerabilities') or []:
                records.append(finding(tool, item['VulnerabilityID'], path, item.get('Severity', 'unknown'),
                                       package=item['PkgName'], version=item.get('InstalledVersion') or '',
                                       fixed=item.get('FixedVersion') or ''))
    else:
        raise ValueError('Unsupported scanner')
    unique = {}
    for record in records:
        previous = unique.get(record['id'])
        if previous is None or record['severity'] == 'unknown' or SEVERITIES[record['severity']] > SEVERITIES[previous['severity']]:
            unique[record['id']] = record
    return sorted(unique.values(), key=lambda r: r['id'])


def rule_files():
    return sorted(p for p in (ROOT / 'rules/semgrep/python').rglob('*')
                  if p.suffix in ('.yaml', '.yml') and not p.name.endswith(('.test.yaml', '.test.yml')))


def policy_digest():
    paths = [ROOT / 'rules/secrets/gitleaks-default/gitleaks.toml',
             ROOT / 'tools/dso/scanning.py', ROOT / 'tools/dso/runtime.py', *rule_files()]
    return digest([(str(p.relative_to(ROOT)), hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths])


def trivy_cache(work):
    """Reuse DSO_CACHE_DIR when this UID can write it (e.g. image volume); otherwise a private cache."""
    shared = os.environ.get('DSO_CACHE_DIR')
    if shared and Path(shared).is_dir() and os.access(shared, os.W_OK | os.X_OK):
        return shared
    return str(work / 'cache')


def scan_repo(path, tools=None, engine='native', timeout=300, project=None, cancel=None, exclusions=()):
    names = selected_tools(tools)
    text(str(path), 'target', 4096)
    text(project, 'project', 200)
    if engine not in ('native', 'docker') or type(timeout) is not int or not 1 <= timeout <= 1800:
        raise ValueError('Invalid engine or timeout (1–1800 seconds per scanner)')
    target = Path(path).resolve(strict=True)
    report = {'schema_version': 2, 'project': project,
              'created_at': datetime.now(timezone.utc).isoformat(),
              'coverage': {'tools': names, 'policy_digest': policy_digest(), 'profile': PROFILE,
                           'engine': engine, 'versions': {n: TOOLS[n][0] for n in names},
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
            report['runs'] = [{'tool': n, 'status': 'error', 'finding_count': 0, 'exit_code': None,
                               'error_code': exc.code, 'error': str(exc)} for n in names]
            return report
        # Only trusted rule files are exposed to the scanners, never the whole kit.
        config_path = work / 'config'
        config_path.mkdir(mode=0o700)
        rules = rule_files()
        if not rules:
            raise ValueError('No trusted Semgrep rules found')
        for i, rule in enumerate(rules):
            shutil.copyfile(rule, config_path / f'rule-{i}.yaml')
        config_text = (ROOT / 'rules/secrets/gitleaks-default/gitleaks.toml').read_text()
        # Remove the upstream broad path allowlist entry, without editing its import.
        config_text = config_text.replace("    \"\"\"gitleaks\\.toml\"\"\",\n".replace('"', "'"), '')
        (config_path / 'gitleaks.toml').write_text(config_text)
        (work / 'empty.yaml').write_text('{}\n')
        (work / 'empty.ignore').write_text('')
        token = os.urandom(24).hex()
        (source_path / '.dso-sentinel').write_text(token)
        (work / 'sentinel').write_text(token)
        docker = executable_path('docker') if engine == 'docker' else None
        for name in names:
            check_cancel(cancel)
            run = {'tool': name, 'status': 'error', 'finding_count': 0, 'exit_code': None}
            container_name = 'dso-' + os.urandom(12).hex()
            try:
                executable = executable_path(name) if engine == 'native' else docker
                if not executable:
                    raise ScanError('missing_executable', 'Scanner executable unavailable')
                if name == 'semgrep':
                    check_python(source_path)
                source = str(source_path) if engine == 'native' else '/src'
                config = str(work) if engine == 'native' else '/work'
                output = config + '/result.json'
                if engine == 'native':
                    rc, version = run_process([executable, 'version' if name == 'gitleaks' else '--version'], work, min(timeout, 15), cancel)
                    match = re.search(r'(?<![0-9])[0-9]+\.[0-9]+\.[0-9]+(?![0-9])', version)
                    if rc or not match or match.group() != TOOLS[name][0]:
                        raise ScanError('version', 'Scanner version differs from reviewed version ' + TOOLS[name][0])
                commands = {
                    'gitleaks': ['dir', '--no-banner', '--redact=0', '--exit-code', '10',
                                 '--config', config + '/config/gitleaks.toml',
                                 '--ignore-gitleaks-allow', '--gitleaks-ignore-path', config + '/empty.ignore',
                                 '--report-format', 'json', '--report-path', output, source],
                    'semgrep': ['scan', '--metrics=off', '--disable-version-check', '--strict',
                                '--disable-nosem', '--no-rewrite-rule-ids', '--no-git-ignore',
                                '--max-target-bytes', '0', '--json', '--output', output,
                                *[v for i in range(len(rules)) for v in ('--config', config + f'/config/rule-{i}.yaml')], source],
                    'trivy': ['fs', '--config', config + '/empty.yaml', '--scanners', 'vuln',
                              '--offline-scan', '--cache-dir', trivy_cache(work) if engine == 'native' else '/work/cache',
                              '--ignorefile', config + '/empty.ignore', '--format', 'json',
                              '--exit-code', '0', '--output', output, source],
                }
                args = [executable, *commands[name]]
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
                    if name != 'trivy':
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
                    probe = ['--entrypoint', '/bin/sh', TOOLS[name][1], '-c',
                             'test "$(cat /work/sentinel)" = "$1" && test "$(cat /src/.dso-sentinel)" = "$1"', 'sh', token]
                    rc, _ = run_process(prefix + probe, work, timeout, cancel)
                    if rc:
                        raise ScanError('mount_visibility', 'Docker cannot read the private snapshot; daemon and client need identical shared TMPDIR paths')
                    args = prefix + [TOOLS[name][1], *(['semgrep'] if name == 'semgrep' else []), *commands[name]]
                (work / 'result.json').unlink(missing_ok=True)
                code, _ = run_process(args, work, timeout, cancel)
                run['exit_code'] = code
                if code not in ({0, 10} if name == 'gitleaks' else {0}):
                    raise ScanError('execution', 'Scanner failed; exit code is recorded separately')
                try:
                    with (work / 'result.json').open('rb') as stream:
                        data = loads(stream.read(20 * 1024 * 1024 + 1))
                    records = normalize(name, data, Path(source))
                except (OSError, ValueError, KeyError, TypeError, AttributeError):
                    raise ScanError('report', 'Scanner report is missing, invalid or incomplete') from None
                if name == 'gitleaks' and bool(records) != (code == 10):
                    raise ScanError('report', 'Gitleaks exit status disagrees with report')
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


def validate_report(report):
    """Validate a bounded v2 snapshot. Structural validity is not authenticity."""
    try:
        if not isinstance(report, dict) or set(report) != {'schema_version', 'project', 'created_at', 'coverage', 'input', 'complete', 'runs', 'findings'}:
            raise ValueError('Unexpected report fields; a v2 report is required')
        if type(report['schema_version']) is not int or report['schema_version'] != 2 or type(report['complete']) is not bool:
            raise ValueError('Unsupported report')
        text(report['project'], 'project', 200)
        stamp = text(report['created_at'], 'timestamp', 40)
        if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|\+00:00)', stamp):
            raise ValueError('created_at must be a UTC timestamp')
        try:
            created = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid UTC timestamp') from None
        if created > datetime.now(timezone.utc):
            raise ValueError('Report timestamp is in the future')
        coverage = report['coverage']
        if not isinstance(coverage, dict) or set(coverage) != {'tools', 'policy_digest', 'profile', 'engine', 'versions', 'exclusions', 'default_exclusions'}:
            raise ValueError('Unexpected coverage fields')
        if not isinstance(coverage['tools'], list):
            raise ValueError('coverage.tools must be a list')
        names = selected_tools(coverage['tools'])
        if names != coverage['tools']:
            raise ValueError('coverage.tools must be sorted')
        if not isinstance(coverage['policy_digest'], str) or not re.fullmatch('[a-f0-9]{64}', coverage['policy_digest']) or coverage['policy_digest'] == '0' * 64:
            raise ValueError('Invalid policy digest')
        if coverage['profile'] != PROFILE or coverage['engine'] not in ('native', 'docker'):
            raise ValueError('Unrecognized coverage profile or engine')
        if not isinstance(coverage['versions'], dict) or set(coverage['versions']) != set(names):
            raise ValueError('Invalid versions')
        if not all(isinstance(v, str) and re.fullmatch(r'\d+\.\d+\.\d+', v) for v in coverage['versions'].values()):
            raise ValueError('Invalid scanner versions')
        if coverage['default_exclusions'] != sorted(EXCLUDED):
            raise ValueError('Unrecognized default exclusions')
        if not isinstance(coverage['exclusions'], list) or len(coverage['exclusions']) > 100:
            raise ValueError('Invalid exclusions')
        for value in coverage['exclusions']:
            if relative_path(value, Path('/unused')) != value or Path(value).is_absolute():
                raise ValueError('Invalid exclusion')
        if coverage['exclusions'] != sorted(set(coverage['exclusions'])):
            raise ValueError('Exclusions must be sorted and unique')
        evidence = report['input']
        if not isinstance(evidence, dict) or set(evidence) != {'files', 'bytes', 'sha256'}:
            raise ValueError('Invalid snapshot evidence')
        if any(type(evidence[k]) is not int or evidence[k] < 0 for k in ('files', 'bytes')):
            raise ValueError('Invalid snapshot counts')
        if not isinstance(evidence['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', evidence['sha256']):
            raise ValueError('Invalid snapshot digest')
        if report['complete'] and evidence['sha256'] == '0' * 64:
            raise ValueError('Complete scan has no snapshot evidence')
        if not isinstance(report['runs'], list) or sorted(r['tool'] for r in report['runs']) != names:
            raise ValueError('Missing or duplicate scanner run')
        if any(r['status'] not in ('complete', 'error') for r in report['runs']):
            raise ValueError('Invalid run status')
        if report['complete'] != all(r['status'] == 'complete' for r in report['runs']):
            raise ValueError('Inconsistent scan completion')
        if not isinstance(report['findings'], list) or len(report['findings']) > 50000:
            raise ValueError('Invalid or excessive findings')
        seen = set()
        for f in report['findings']:
            if f['tool'] not in names or f['severity'] not in SEVERITIES:
                raise ValueError('Invalid finding tool or severity')
            if Path(f['path']).is_absolute():
                raise ValueError('Absolute finding path')
            expected = finding(f['tool'], f['rule_id'], relative_path(f['path'], Path('/unused')),
                               f['severity'], f['line'], f['package'], f['installed_version'], f['fixed_version'], f['fingerprint'])
            if f != expected or f['id'] in seen:
                raise ValueError('Invalid or duplicate finding')
            if f['tool'] == 'gitleaks':
                if f['severity'] != 'high' or not f['fingerprint'] or f['line'] < 1 or any(f[k] for k in ('package', 'installed_version', 'fixed_version')):
                    raise ValueError('Invalid secret finding')
            elif f['fingerprint']:
                raise ValueError('Unexpected secret fingerprint')
            if f['tool'] == 'semgrep' and (f['line'] < 1 or any(f[k] for k in ('package', 'installed_version', 'fixed_version'))):
                raise ValueError('Invalid SAST finding')
            if f['tool'] == 'trivy' and (f['line'] != 0 or not f['package']):
                raise ValueError('Invalid dependency finding')
            seen.add(f['id'])
        if [f['id'] for f in report['findings']] != sorted(seen):
            raise ValueError('Findings must be sorted')
        for run in report['runs']:
            required = {'tool', 'status', 'finding_count', 'exit_code'}
            expected_fields = required if run['status'] == 'complete' else required | {'error_code', 'error'}
            if set(run) != expected_fields:
                raise ValueError('Unexpected scanner run fields')
            if type(run['finding_count']) is not int or run['finding_count'] != sum(f['tool'] == run['tool'] for f in report['findings']):
                raise ValueError('Inconsistent finding count')
            code = run['exit_code']
            if code is not None and (type(code) is not int or not -255 <= code <= 255):
                raise ValueError('Invalid scanner exit code')
            if run['status'] == 'complete':
                expected_code = 10 if run['tool'] == 'gitleaks' and run['finding_count'] else 0
                if code != expected_code:
                    raise ValueError('Completed run contradicts scanner exit code')
            else:
                text(run['error_code'], 'error code', 64)
                text(run['error'], 'error description', 512)
                if run['finding_count']:
                    raise ValueError('Incomplete scanner cannot contribute normalized findings')
    except (KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ValueError('Malformed DSO report') from exc
    return report


def gate(report, baseline=None, fail_on='high'):
    if fail_on not in SEVERITIES or fail_on == 'unknown':
        raise ValueError('Invalid severity threshold')
    validate_report(report)
    if baseline is not None:
        validate_report(baseline)
    mismatch, changes = [], []
    if baseline is not None:
        if report['project'] != baseline['project']:
            mismatch.append('project')
        # A baseline only accepts exact finding IDs, so a kit/policy/tool change can
        # only turn accepted findings into new ones. Report it instead of failing every MR.
        changes = ['coverage.' + k for k in report['coverage'] if report['coverage'][k] != baseline['coverage'][k]]
    comparable = baseline is not None and not mismatch and baseline['complete']
    previous = {f['id']: f for f in baseline['findings']} if comparable else {}
    current = {f['id']: f for f in report['findings']}
    new = [f for f in report['findings'] if f['id'] not in previous or f['severity'] == 'unknown' or
           previous[f['id']]['severity'] == 'unknown' or SEVERITIES[f['severity']] > SEVERITIES[previous[f['id']]['severity']]]
    blocking = [f for f in new if f['severity'] == 'unknown' or SEVERITIES[f['severity']] >= SEVERITIES[fail_on]]
    incomplete = not report['complete'] or (baseline is not None and not baseline['complete']) or bool(mismatch)
    return {'exit_code': 2 if incomplete else (1 if blocking else 0),
            'status': 'incomparable' if mismatch else ('incomplete' if incomplete else ('blocked' if blocking else 'passed')),
            'mismatch': mismatch, 'coverage_changes': changes,
            'new_or_escalated': len(new), 'existing': len(report['findings']) - len(new),
            'blocking': blocking,
            'resolved': [i for i in previous if i not in current] if report['complete'] else [],
            'fix_changed': [f['id'] for f in report['findings'] if f['id'] in previous and f['fixed_version'] != previous[f['id']]['fixed_version']]}


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
