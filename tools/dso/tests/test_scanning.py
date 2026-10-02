import copy
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
import runtime  # noqa: E402
import scanning as core  # noqa: E402

PEM = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA\n-----END RSA PRIVATE KEY-----'


def secret(rule='test-token', path='app.py', line=2, value='one'):
    return core.normalize('gitleaks', [{'RuleID': rule, 'File': '/src/' + path, 'StartLine': line,
                                        'Secret': value}], Path('/src'))[0]


def report(findings=None, tools=None, project='fixture'):
    names = tools or ['gitleaks']
    findings = sorted(findings or [], key=lambda f: f['id'])
    counts = {n: sum(f['tool'] == n for f in findings) for n in names}
    return {'schema_version': 2, 'project': project, 'created_at': '2026-10-02T00:00:00+00:00',
            'coverage': {'tools': names, 'policy_digest': 'a' * 64, 'profile': core.PROFILE, 'engine': 'native',
                         'versions': {n: core.TOOLS[n][0] for n in names}, 'exclusions': [],
                         'default_exclusions': sorted(core.EXCLUDED)},
            'input': {'files': 1, 'bytes': 1, 'sha256': 'b' * 64}, 'complete': True,
            'runs': [{'tool': n, 'status': 'complete', 'finding_count': counts[n],
                      'exit_code': 10 if n == 'gitleaks' and counts[n] else 0} for n in names],
            'findings': findings}


class AdapterTests(unittest.TestCase):
    def test_gitleaks_redaction_deduplication_and_multiline_secret(self):
        raw = {'RuleID': 'test-token', 'File': '/src/app.py', 'StartLine': 2,
               'Secret': 'DO-NOT-RETURN', 'Match': 'DO-NOT-RETURN'}
        pem = {'RuleID': 'private-key', 'File': '/src/id_rsa', 'StartLine': 1, 'Secret': PEM}
        result = core.normalize('gitleaks', [raw, raw, pem], Path('/src'))
        self.assertEqual(len(result), 2)
        self.assertEqual({f['path'] for f in result}, {'app.py', 'id_rsa'})
        self.assertNotIn('DO-NOT-RETURN', json.dumps(result))
        self.assertNotIn('MIIEow', json.dumps(result))

    def test_rotated_secret_at_same_location_is_new(self):
        self.assertNotEqual(secret(value='one')['id'], secret(value='two')['id'])

    def test_semgrep_and_trivy(self):
        def results(*severities, same_line=False):
            return {'results': [{'check_id': 'python.test', 'path': '/project/app.py',
                                 'start': {'line': 3 if same_line else line},
                                 'extra': {'severity': severity, 'lines': 'private'}}
                                for line, severity in enumerate(severities, 1)], 'errors': []}
        findings = core.normalize('semgrep', results('ERROR', 'CRITICAL', 'LOW', 'BOGUS'), Path('/project'))
        self.assertEqual({f['line']: f['severity'] for f in findings},
                         {1: 'high', 2: 'critical', 3: 'low', 4: 'unknown'})
        self.assertNotIn('private', json.dumps(findings))
        merged = core.normalize('semgrep', results('CRITICAL', 'BOGUS', same_line=True), Path('/project'))
        self.assertEqual([f['severity'] for f in merged], ['unknown'])
        data = {'SchemaVersion': 2, 'ArtifactName': '/project', 'Results': [
            {'Target': 'requirements.txt', 'Vulnerabilities': [
                {'VulnerabilityID': 'CVE-TEST', 'PkgName': 'example', 'InstalledVersion': '1',
                 'FixedVersion': None, 'Severity': 'CRITICAL'}]}]}
        f = core.normalize('trivy', data, Path('/project'))[0]
        self.assertEqual((f['fixed_version'], f['severity']), ('', 'critical'))

    def test_incomplete_and_malformed_reports_rejected(self):
        for tool, data in [('gitleaks', {}), ('semgrep', {'results': [], 'errors': [{}]}),
                           ('semgrep', {'results': []}), ('trivy', {}),
                           ('gitleaks', [{'RuleID': 'r', 'File': '/src/a', 'StartLine': 1, 'Secret': ''}])]:
            with self.subTest(tool=tool), self.assertRaises((ValueError, KeyError)):
                core.normalize(tool, data, Path('/src'))
        for value in ('../escape', '/other/app.py', '.'):
            with self.assertRaises(ValueError):
                core.relative_path(value, Path('/project'))


class GateTests(unittest.TestCase):
    def setUp(self):
        self.f = secret()

    def test_all_new_existing_and_escalated(self):
        current = report([self.f])
        self.assertEqual(core.gate(current)['exit_code'], 1)
        self.assertEqual(core.gate(current, current)['exit_code'], 0)
        trivy = core.finding('trivy', 'CVE-1', 'requirements.txt', 'medium', 0, 'pkg', '1')
        before = report([trivy], tools=['trivy'])
        after = report([dict(core.finding('trivy', 'CVE-1', 'requirements.txt', 'high', 0, 'pkg', '1'))], tools=['trivy'])
        self.assertEqual(core.gate(after, before)['exit_code'], 1)
        result = core.gate(report(), current)
        self.assertEqual((result['exit_code'], result['resolved']), (0, [self.f['id']]))

    def test_unknown_blocks_even_with_baseline(self):
        unknown = core.finding('trivy', 'CVE-1', 'requirements.txt', 'unknown', 0, 'pkg', '1')
        critical = core.finding('trivy', 'CVE-1', 'requirements.txt', 'critical', 0, 'pkg', '1')
        self.assertEqual(core.gate(report([unknown], ['trivy']), fail_on='critical')['exit_code'], 1)
        self.assertEqual(core.gate(report([unknown], ['trivy']), report([unknown], ['trivy']))['exit_code'], 1)
        self.assertEqual(core.gate(report([critical], ['trivy']), report([unknown], ['trivy']))['exit_code'], 1)
        low = core.finding('trivy', 'CVE-2', 'requirements.txt', 'low', 0, 'pkg', '1')
        self.assertEqual(core.gate(report([low], ['trivy']))['exit_code'], 0)

    def test_incomplete_current_or_baseline_cannot_pass_but_shows_blocking(self):
        bad = report()
        bad['complete'] = False
        bad['runs'][0].update(status='error', error_code='timeout', error='Scanner exceeded its timeout')
        self.assertEqual(core.gate(bad)['exit_code'], 2)
        partial = report([self.f, core.finding('trivy', 'CVE-1', 'r.txt', 'high', 0, 'pkg', '1')], ['gitleaks', 'trivy'])
        partial['complete'] = False
        partial['findings'] = [f for f in partial['findings'] if f['tool'] == 'gitleaks']
        partial['runs'][1].update(status='error', finding_count=0, error_code='timeout', error='timeout')
        result = core.gate(partial)
        self.assertEqual((result['exit_code'], len(result['blocking'])), (2, 1))
        self.assertEqual(core.gate(report(), bad)['exit_code'], 2)

    def test_project_mismatch_rejected_but_coverage_change_is_reported(self):
        result = core.gate(report(), report(project='other'))
        self.assertEqual((result['exit_code'], result['mismatch']), (2, ['project']))
        baseline = report([self.f])
        baseline['coverage']['policy_digest'] = 'c' * 64
        result = core.gate(report([self.f]), baseline)
        self.assertEqual((result['exit_code'], result['coverage_changes']), (0, ['coverage.policy_digest']))

    def test_tampered_and_contradictory_reports_rejected(self):
        for mutate in [lambda r: r['findings'][0].update(id='fake'),
                       lambda r: r['findings'].append(r['findings'][0]),
                       lambda r: r.update(runs=[]),
                       lambda r: r['runs'][0].update(finding_count=0),
                       lambda r: r['runs'][0].update(exit_code=2),
                       lambda r: r['coverage'].update(tools=None),
                       lambda r: r['coverage'].update(policy_digest='0' * 64),
                       lambda r: r.update(created_at='2026-10-02'),
                       lambda r: r['findings'][0].update(severity='info'),
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
    def fake_run(self, args, cwd, timeout, cancel=None, **kwargs):
        name = Path(args[0]).name
        if args[1] in ('version', '--version'):
            return 0, core.TOOLS[name][0]
        flag = '--report-path' if name == 'gitleaks' else '--output'
        output = Path(args[args.index(flag) + 1])
        data = {'gitleaks': [], 'semgrep': {'results': [], 'errors': []},
                'trivy': {'SchemaVersion': 2, 'ArtifactName': '/src'}}[name]
        output.write_text(json.dumps(data))
        return 0, ''

    def test_all_scanners_complete_and_no_shell(self):
        with tempfile.TemporaryDirectory(prefix='dso space ; ') as folder, \
             patch.object(core.shutil, 'which', side_effect=lambda n, **kw: '/tools/' + n), \
             patch.object(core, 'run_process', side_effect=self.fake_run) as run:
            Path(folder, 'app.py').write_text('print(1)\n')
            result = core.scan_repo(folder, project='fixture')
            self.assertTrue(result['complete'], result['runs'])
            self.assertEqual(result['input']['files'], 1)
            self.assertEqual(core.gate(result)['exit_code'], 0)
            for call in run.call_args_list:
                self.assertIsInstance(call.args[0], list)
            semgrep_args = next(c.args[0] for c in run.call_args_list if c.args[0][1] == 'scan')
            self.assertIn('--strict', semgrep_args)
            self.assertIn('--no-git-ignore', semgrep_args)

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
            missing_project = [sys.executable, str(ROOT / 'tools/dso/dso.py'), 'scan', 'repo', folder,
                               '--output', str(Path(folder) / 'out.json')]
            self.assertEqual(subprocess.run(missing_project, capture_output=True).returncode, 2)

    def test_duplicate_empty_and_unknown_tools_rejected(self):
        for names in [[], ['sh'], ['gitleaks', 'gitleaks']]:
            with self.assertRaises(ValueError):
                core.selected_tools(names)


if __name__ == '__main__':
    unittest.main()
