import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/dso'))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
import manifest  # noqa: E402
import reports  # noqa: E402
import runtime  # noqa: E402
import scanning as core  # noqa: E402

PEM = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA\n-----END RSA PRIVATE KEY-----'


def secret(rule='test-token', path='app.py', line=2, value='one'):
    return core.normalize('gitleaks', [{'RuleID': rule, 'File': '/src/' + path, 'StartLine': line,
                                        'Secret': value}], '/src')[0]


def dependency(rule='CVE-2024-0001', severity='high', package='pkg', version='1', fixed=''):
    return reports.finding('trivy', rule, 'requirements.txt', severity, 0, package, version, fixed)


def report(findings=None, plugins=None, project='fixture'):
    names = plugins or ['gitleaks']
    findings = sorted(findings or [], key=lambda f: f['id'])
    counts = {n: sum(f['plugin'] == n for f in findings) for n in names}
    return {'schema_version': 3, 'project': project, 'target': {'type': 'repo'},
            'created_at': '2026-10-02T00:00:00+00:00',
            'coverage': {'profile': core.DEFAULT_PROFILE, 'plugins': names,
                         'versions': {n: manifest.plugin(n)['version'] for n in names}, 'engine': 'native',
                         'policy_digest': 'a' * 64, 'exclusions': [], 'default_exclusions': sorted(core.EXCLUDED)},
            'input': {'files': 1, 'bytes': 1, 'sha256': 'b' * 64}, 'complete': True,
            'runs': [{'plugin': n, 'status': 'complete', 'finding_count': counts[n],
                      'exit_code': 10 if n == 'gitleaks' and counts[n] else 0} for n in names],
            'findings': findings}


class AdapterTests(unittest.TestCase):
    def test_gitleaks_redaction_deduplication_and_multiline_secret(self):
        raw = {'RuleID': 'test-token', 'File': '/src/app.py', 'StartLine': 2,
               'Secret': 'DO-NOT-RETURN', 'Match': 'DO-NOT-RETURN'}
        pem = {'RuleID': 'private-key', 'File': '/src/id_rsa', 'StartLine': 1, 'Secret': PEM}
        result = core.normalize('gitleaks', [raw, raw, pem], '/src')
        self.assertEqual(len(result), 2)
        self.assertEqual({f['path'] for f in result}, {'app.py', 'id_rsa'})
        self.assertNotIn('DO-NOT-RETURN', json.dumps(result))
        self.assertNotIn('MIIEow', json.dumps(result))

    def test_rotated_secret_at_same_location_is_new(self):
        self.assertNotEqual(secret(value='one')['id'], secret(value='two')['id'])

    def test_finding_ids_are_unchanged_from_report_v2(self):
        # v2 baselines accepted these exact IDs; renaming tool to plugin must not reset them.
        f = secret()
        fingerprint = hashlib.sha256(b'dso-secret-v2\0test-token\0one').hexdigest()
        legacy = json.dumps(['gitleaks', 'test-token', 'app.py', 2, '', '', fingerprint], sort_keys=True, separators=(',', ':'))
        self.assertEqual((f['fingerprint'], f['id']), (fingerprint, hashlib.sha256(legacy.encode()).hexdigest()))

    def test_semgrep_and_trivy(self):
        def results(*severities, same_line=False):
            return {'results': [{'check_id': 'python.test', 'path': '/project/app.py',
                                 'start': {'line': 3 if same_line else line},
                                 'extra': {'severity': severity, 'lines': 'private', 'message': 'private'}}
                                for line, severity in enumerate(severities, 1)], 'errors': []}
        findings = core.normalize('semgrep', results('ERROR', 'CRITICAL', 'LOW', 'BOGUS'), '/project')
        self.assertEqual({f['line']: f['severity'] for f in findings},
                         {1: 'high', 2: 'critical', 3: 'low', 4: 'unknown'})
        self.assertNotIn('private', json.dumps(findings))
        merged = core.normalize('semgrep', results('CRITICAL', 'BOGUS', same_line=True), '/project')
        self.assertEqual([f['severity'] for f in merged], ['unknown'])
        data = {'SchemaVersion': 2, 'ArtifactName': '/project', 'Results': [
            {'Target': 'requirements.txt', 'Vulnerabilities': [
                {'VulnerabilityID': 'CVE-TEST', 'PkgName': 'example', 'InstalledVersion': '1',
                 'FixedVersion': None, 'Severity': 'CRITICAL', 'Description': 'private'}]}]}
        f = core.normalize('trivy', data, '/project')[0]
        self.assertEqual((f['fixed_version'], f['severity'], f['category']), ('', 'critical', 'sca'))
        self.assertNotIn('private', json.dumps(f))

    def test_cwe_and_references_come_only_from_validated_identifiers(self):
        semgrep = {'results': [{'check_id': 'python.tls', 'path': '/p/app.py', 'start': {'line': 1},
                                'extra': {'severity': 'ERROR', 'metadata': {'cwe': [
                                    'CWE-295: Improper Certificate Validation', 'CWE-79"><script>', 'not a cwe', 7]}}}],
                   'errors': []}
        f = core.normalize('semgrep', semgrep, '/p')[0]
        self.assertEqual((f['category'], f['cwe']), ('sast', ['CWE-79', 'CWE-295']))
        self.assertEqual(f['references'], ['https://cwe.mitre.org/data/definitions/79.html',
                                           'https://cwe.mitre.org/data/definitions/295.html'])
        trivy = {'SchemaVersion': 2, 'ArtifactName': '/p', 'Results': [{'Target': 'go.mod', 'Vulnerabilities': [
            {'VulnerabilityID': 'CVE-2024-24790', 'PkgName': 'stdlib', 'Severity': 'HIGH', 'CweIDs': ['CWE-20', '<b>']},
            {'VulnerabilityID': 'GHSA-xxxx-yyyy-zzzz', 'PkgName': 'a', 'Severity': 'LOW'},
            {'VulnerabilityID': 'GHSA-2234-5678-9cfg', 'PkgName': 'b', 'Severity': 'LOW', 'CweIDs': 'CWE-1'},
            {'VulnerabilityID': 'CVE-2024-1"><img src=x>', 'PkgName': 'c', 'Severity': 'LOW'}]}]}
        by_rule = {f['rule_id']: f for f in core.normalize('trivy', trivy, '/p')}
        self.assertEqual(by_rule['CVE-2024-24790']['references'],
                         ['https://nvd.nist.gov/vuln/detail/CVE-2024-24790', 'https://cwe.mitre.org/data/definitions/20.html'])
        self.assertEqual(by_rule['GHSA-2234-5678-9cfg']['references'], ['https://github.com/advisories/GHSA-2234-5678-9cfg'])
        self.assertEqual(by_rule['GHSA-xxxx-yyyy-zzzz']['references'], [])
        self.assertEqual(by_rule['CVE-2024-1"><img src=x>']['references'], [])
        self.assertEqual((secret()['category'], secret()['cwe']), ('secret', ['CWE-798']))

    def test_incomplete_and_malformed_reports_rejected(self):
        for plugin, data in [('gitleaks', {}), ('semgrep', {'results': [], 'errors': [{}]}),
                             ('semgrep', {'results': []}), ('trivy', {}),
                             ('gitleaks', [{'RuleID': 'r', 'File': '/src/a', 'StartLine': 1, 'Secret': ''}])]:
            with self.subTest(plugin=plugin), self.assertRaises((ValueError, KeyError)):
                core.normalize(plugin, data, '/src')
        for value in ('../escape', '/other/app.py', '.'):
            with self.assertRaises(ValueError):
                reports.relative_path(value, Path('/project'))


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(manifest.PATH.read_text())

    def test_shipped_manifest_profiles_and_kit_paths(self):
        manifest.validate(copy.deepcopy(self.data))
        self.assertIn(core.DEFAULT_PROFILE, manifest.profiles())
        for value in manifest.kit_paths():
            self.assertTrue((ROOT / value).exists(), value)

    def test_unsafe_or_inconsistent_manifests_rejected(self):
        cases = [
            lambda d: d['plugins']['trivy'].update(image=d['plugins']['trivy']['image'].split('@')[0]),
            lambda d: d['plugins']['trivy'].update(image=d['plugins']['trivy']['image'].replace(':0.75.0@', ':latest@')),
            lambda d: d['plugins']['trivy'].update(category='magic'),
            lambda d: d['plugins']['trivy'].update(adapter='../../evil'),
            lambda d: d['plugins']['trivy'].update(extra=True),
            lambda d: d['plugins']['trivy'].update(network='yes'),
            lambda d: d['plugins']['trivy']['install']['binaries']['linux/amd64'].update(url='https://example.com/trivy.tgz'),
            lambda d: d['plugins']['gitleaks']['install']['binaries']['linux/amd64'].update(sha256='0' * 63),
            lambda d: d['plugins']['gitleaks'].update(severity={'fixed': 'urgent'}),
            lambda d: d['plugins']['gitleaks'].update(cwe=['CWE-0']),
            lambda d: d['plugins']['gitleaks'].update(manual='../README.md'),
            lambda d: d['plugins'].update({'trivy-fs': dict(d['plugins']['trivy'], version_args=['version'])}),
            lambda d: d['profiles']['ci-blocking']['plugins'].update(missing={}),
            lambda d: d['profiles']['ci-blocking']['plugins']['semgrep'].update(rules=['../../etc']),
            lambda d: d['profiles']['ci-blocking']['plugins']['semgrep'].update(rules=['tools/dso']),
            lambda d: d['profiles']['ci-blocking']['plugins']['semgrep'].update(rules=['rules/semgrep/missing']),
            lambda d: d['profiles']['ci-blocking']['plugins']['gitleaks'].update(config='rules/semgrep/python'),
            lambda d: d['profiles']['ci-blocking']['plugins']['trivy'].update(rules=['rules/semgrep/python']),
            lambda d: d['profiles']['ci-blocking'].update(target='image'),
        ]
        for i, mutate in enumerate(cases):
            data = copy.deepcopy(self.data)
            mutate(data)
            with self.subTest(case=i), self.assertRaises(ValueError):
                manifest.validate(data)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.f = secret()

    def test_all_new_existing_and_escalated(self):
        current = report([self.f])
        self.assertEqual(core.gate(current)['exit_code'], 1)
        self.assertEqual(core.gate(current, current)['exit_code'], 0)
        before = report([dependency(severity='medium')], plugins=['trivy'])
        after = report([dependency(severity='high')], plugins=['trivy'])
        self.assertEqual(core.gate(after, before)['exit_code'], 1)
        result = core.gate(report(), current)
        self.assertEqual((result['exit_code'], result['resolved']), (0, [self.f['id']]))

    def test_unknown_blocks_even_with_baseline(self):
        unknown, critical = dependency(severity='unknown'), dependency(severity='critical')
        self.assertEqual(core.gate(report([unknown], ['trivy']), fail_on='critical')['exit_code'], 1)
        self.assertEqual(core.gate(report([unknown], ['trivy']), report([unknown], ['trivy']))['exit_code'], 1)
        self.assertEqual(core.gate(report([critical], ['trivy']), report([unknown], ['trivy']))['exit_code'], 1)
        low = dependency('CVE-2024-0002', 'low')
        self.assertEqual(core.gate(report([low], ['trivy']))['exit_code'], 0)

    def test_incomplete_current_or_baseline_cannot_pass_but_shows_blocking(self):
        bad = report()
        bad['complete'] = False
        bad['runs'][0].update(status='error', error_code='timeout', error='Scanner exceeded its timeout')
        self.assertEqual(core.gate(bad)['exit_code'], 2)
        partial = report([self.f, dependency()], ['gitleaks', 'trivy'])
        partial['complete'] = False
        partial['findings'] = [f for f in partial['findings'] if f['plugin'] == 'gitleaks']
        partial['runs'][1].update(status='error', finding_count=0, error_code='timeout', error='timeout')
        result = core.gate(partial)
        self.assertEqual((result['exit_code'], len(result['blocking'])), (2, 1))
        self.assertEqual(core.gate(report(), bad)['exit_code'], 2)

    def test_project_mismatch_and_narrowed_coverage_cannot_pass(self):
        result = core.gate(report(), report(project='other'))
        self.assertEqual((result['exit_code'], result['mismatch']), (2, ['project']))
        old = report([dependency()], plugins=['gitleaks', 'trivy'])
        result = core.gate(report(plugins=['gitleaks']), old)
        self.assertEqual((result['exit_code'], result['status'], result['mismatch'], result['resolved']),
                         (2, 'incomparable', ['coverage.plugins'], []))
        excluded = report([self.f])
        excluded['coverage']['exclusions'] = ['vendor']
        self.assertEqual(core.gate(excluded, report([self.f]))['mismatch'], ['coverage.exclusions'])
        # audit runs more Semgrep rules than ci-blocking; going back drops rule directories.
        audit = report([self.f], plugins=['gitleaks', 'semgrep'])
        audit['coverage']['profile'] = 'audit'
        narrower = report([self.f], plugins=['gitleaks', 'semgrep'])
        self.assertEqual(core.gate(narrower, audit)['mismatch'], ['coverage.profile'])
        widened = core.gate(audit, narrower)
        self.assertEqual((widened['exit_code'], widened['mismatch'], widened['coverage_changes']), (0, [], ['coverage.profile']))

    def test_updates_and_wider_coverage_stay_comparable(self):
        baseline = report([self.f], plugins=['gitleaks'])
        baseline['coverage']['exclusions'] = ['vendor']
        current = report([self.f, dependency()], plugins=['gitleaks', 'trivy'])
        current['coverage'].update(policy_digest='c' * 64, engine='docker')
        current['coverage']['versions']['gitleaks'] = '9.0.0'
        result = core.gate(current, baseline)
        self.assertEqual((result['exit_code'], result['status'], result['mismatch'], result['new_or_escalated']),
                         (1, 'blocked', [], 1))
        self.assertEqual(sorted(result['coverage_changes']),
                         ['coverage.engine', 'coverage.exclusions', 'coverage.plugins', 'coverage.policy_digest',
                          'coverage.versions'])
        self.assertEqual(core.gate(report([self.f], plugins=['gitleaks']), baseline)['exit_code'], 0)

    def test_v2_report_rejected_with_guidance(self):
        legacy = report([self.f])
        legacy['schema_version'] = 2
        with self.assertRaisesRegex(ValueError, 'v2 is no longer accepted'):
            core.gate(legacy)

    def test_tampered_and_contradictory_reports_rejected(self):
        for mutate in [lambda r: r['findings'][0].update(id='fake'),
                       lambda r: r['findings'].append(r['findings'][0]),
                       lambda r: r.update(runs=[]),
                       lambda r: r['runs'][0].update(finding_count=0),
                       lambda r: r['runs'][0].update(exit_code=2),
                       lambda r: r['coverage'].update(plugins=None),
                       lambda r: r['coverage'].update(policy_digest='0' * 64),
                       lambda r: r['coverage'].update(profile='custom'),
                       lambda r: r.update(target={'type': 'image'}),
                       lambda r: r.update(created_at='2026-10-02'),
                       lambda r: r['findings'][0].update(severity='info'),
                       lambda r: r['findings'][0].update(category='sast'),
                       lambda r: r['findings'][0].update(cwe=[]),
                       lambda r: r['findings'][0]['references'].append('https://attacker.example'),
                       lambda r: r.update(complete='true')]:
            r = report([self.f])
            mutate(r)
            with self.assertRaises(ValueError):
                core.gate(r)


class SnapshotTests(unittest.TestCase):
    def snapshot(self, build, exclusions=()):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as work:
            build(Path(source))
            destination = Path(work) / 'snapshot'
            evidence = runtime.snapshot(Path(source), destination, exclusions=exclusions)
            return evidence, sorted(p.relative_to(destination).as_posix() for p in destination.rglob('*'))

    def test_target_ignore_files_are_not_copied(self):
        def build(root):
            (root / 'app.py').write_text('x = 1\n')
            for name in ('.gitleaksignore', '.semgrepignore', '.gitignore'):
                (root / name).write_text('*\n')
            (root / 'node_modules').mkdir()
            (root / 'node_modules/a.py').write_text('x = 1\n')
        evidence, files = self.snapshot(build)
        self.assertEqual(files, ['.semgrepignore', 'app.py'])
        self.assertEqual(evidence['files'], 1)

    def test_symlink_special_file_and_control_characters_fail_unless_excluded(self):
        cases = [(lambda r: (r / 'link').symlink_to('/etc/hosts'), 'symlink'),
                 (lambda r: os.mkfifo(r / 'fifo'), 'special_file'),
                 (lambda r: (r / 'bad\nname').write_text('x'), 'unsupported_path')]
        for build, code in cases:
            with self.subTest(code=code), self.assertRaises(runtime.ScanError) as raised:
                self.snapshot(build)
            self.assertEqual(raised.exception.code, code)
        self.assertEqual(self.snapshot(cases[0][0], exclusions=['link'])[1], ['.semgrepignore'])

    @unittest.skipIf(os.geteuid() == 0, 'root can read every file')
    def test_unreadable_input_is_incomplete_not_silent(self):
        def build(root):
            (root / 'secret.env').write_text('token')
            (root / 'secret.env').chmod(0)
        with self.assertRaises(runtime.ScanError) as raised:
            self.snapshot(build)
        self.assertEqual(raised.exception.code, 'unreadable_input')


class RunnerTests(unittest.TestCase):
    EMPTY = {'gitleaks': [], 'semgrep': {'results': [], 'errors': []},
             'trivy': {'SchemaVersion': 2, 'ArtifactName': '/src'}}

    def fake_run(self, args, cwd, timeout, cancel=None, **kwargs):
        name = Path(args[0]).name
        if args[1] in ('version', '--version'):
            return 0, manifest.plugin(name)['version']
        flag = '--report-path' if name == 'gitleaks' else '--output'
        output = Path(args[args.index(flag) + 1])
        output.write_text(json.dumps(self.EMPTY[name]))
        return 0, ''

    def fake_docker(self, args, cwd, timeout, cancel=None, **kwargs):
        if '--entrypoint' in args or args[1] in ('rm', 'image'):
            return 0, ''
        work = next(Path(a.split(',')[1][4:]) for a in args if a.endswith(',dst=/work'))
        image = next(a for a in args if '@sha256:' in a)
        tool = next(n for n, spec in manifest.plugins().items() if spec['image'] == image)
        output = next(a for a in args if a.startswith('/work/results/') and a.endswith('result.json'))
        (work / output[len('/work/'):]).write_text(json.dumps(self.EMPTY[tool]))
        return 0, ''

    def test_all_scanners_complete_and_no_shell(self):
        with tempfile.TemporaryDirectory(prefix='dso space ; ') as folder, \
             patch.object(core.shutil, 'which', side_effect=lambda n, **kw: '/tools/' + n), \
             patch.object(core, 'run_process', side_effect=self.fake_run) as run:
            Path(folder, 'app.py').write_text('print(1)\n')
            result = core.scan_repo(folder, project='fixture')
            self.assertTrue(result['complete'], result['runs'])
            self.assertEqual((result['input']['files'], result['target']), (1, {'type': 'repo'}))
            self.assertEqual(result['coverage']['plugins'], sorted(manifest.profile(core.DEFAULT_PROFILE)['plugins']))
            self.assertEqual(core.gate(result)['exit_code'], 0)
            for call in run.call_args_list:
                self.assertIsInstance(call.args[0], list)
            semgrep_args = next(c.args[0] for c in run.call_args_list if c.args[0][1] == 'scan')
            self.assertIn('--strict', semgrep_args)
            self.assertIn('--no-git-ignore', semgrep_args)

    def test_docker_isolation_follows_the_manifest(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as cache, \
             patch.dict(os.environ, {'DSO_CACHE_DIR': cache}), \
             patch.object(core.shutil, 'which', side_effect=lambda n, **kw: '/tools/' + n), \
             patch.object(core, 'run_process', side_effect=self.fake_docker) as run:
            Path(folder, 'app.py').write_text('print(1)\n')
            result = core.scan_repo(folder, engine='docker', project='fixture')
            self.assertTrue(result['complete'], result['runs'])
            scans = [c.args[0] for c in run.call_args_list if c.args[0][1] == 'run' and '--entrypoint' not in c.args[0]]
            self.assertEqual(len(scans), 3)
            self.assertFalse(list(Path(cache).glob('.dso-sentinel-*')))
            for args in scans:
                image = next(a for a in args if '@sha256:' in a)
                plugin, spec = next((n, s) for n, s in manifest.plugins().items() if s['image'] == image)
                # Only scanners with a vulnerability database may write the shared cache.
                self.assertEqual(f'type=bind,src={Path(cache).resolve()},dst=/cache' in args, bool(spec['database']), plugin)
                self.assertTrue({'--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges'} <= set(args))
                self.assertEqual('--network' in args, not spec['network'], plugin)
                position = args.index(image)
                self.assertEqual(args[position + 1:position + 1 + len(spec['image_command'])], spec['image_command'])

    def test_missing_binary_failure_missing_report_and_timeout(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(core.shutil, 'which', return_value=None):
                self.assertFalse(core.scan_repo(folder, ['gitleaks'], project='fixture')['complete'])
            for effect in [lambda *a, **k: (2, 'sensitive error'), lambda *a, **k: (0, '8.30.1'),
                           runtime.ScanError('timeout', 'Scanner exceeded its timeout')]:
                with patch.object(core.shutil, 'which', return_value='/bin/gitleaks'), \
                     patch.object(core, 'run_process', side_effect=effect):
                    result = core.scan_repo(folder, ['gitleaks'], project='fixture')
                    self.assertFalse(result['complete'])
                    self.assertNotIn('sensitive', json.dumps(result))
                    core.validate_report(result)

    def test_real_subprocess_timeout_cancel_and_diagnostics(self):
        with self.assertRaises(runtime.ScanError):
            runtime.run_process([sys.executable, '-c', 'import time; time.sleep(10)'], '/tmp', 0.05)
        cancel = threading.Event()
        threading.Timer(0.2, cancel.set).start()
        with self.assertRaises(runtime.Cancelled):
            runtime.run_process([sys.executable, '-c', 'import time; time.sleep(10)'], '/tmp', 10, cancel)
        stderr = 'import sys; sys.stderr.write({!r})'
        self.assertEqual(runtime.run_process([sys.executable, '-c', stderr.format('Ran 3 rules on 429 files')], '/tmp', 10)[0], 0)
        with self.assertRaises(runtime.ScanError) as raised:
            runtime.run_process([sys.executable, '-c', stderr.format('HTTP 429 Too Many Requests')], '/tmp', 10)
        self.assertEqual(raised.exception.code, 'rate_limit')

    def test_private_output_and_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / 'report.json'
            core.write_report(destination, report())
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
            command = [sys.executable, str(ROOT / 'tools/dso/dso.py'), 'gate', '--input', str(destination)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            for content in ('{}', '﻿{}', '[' * 100000):
                destination.write_text(content)
                self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            scan = [sys.executable, str(ROOT / 'tools/dso/dso.py'), 'scan', 'repo', folder,
                    '--output', str(Path(folder) / 'out.json')]
            for extra in ([], ['--project', 'p', '--profile', 'missing'], ['--project', 'p', '--plugins', 'sh']):
                self.assertEqual(subprocess.run(scan + extra, capture_output=True).returncode, 2, extra)

    def test_duplicate_empty_and_unknown_plugins_or_profiles_rejected(self):
        for names in [[], ['sh'], ['gitleaks', 'gitleaks']]:
            with self.assertRaises(ValueError):
                core.selected_plugins(names, core.DEFAULT_PROFILE)
        with tempfile.TemporaryDirectory() as folder, self.assertRaises(ValueError):
            core.scan_repo(folder, project='fixture', profile='missing')


if __name__ == '__main__':
    unittest.main()
