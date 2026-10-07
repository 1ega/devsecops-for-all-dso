"""Regressions where orchestration or normalization can change scan coverage."""
import os
import itertools
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
import manifest
import reports
import runtime
import scanning
from plugins import osv_scanner


class SeverityTests(unittest.TestCase):
    def test_unknown_duplicate_blocks_regardless_of_scanner_order(self):
        findings = [reports.finding('trivy', 'CVE-2026-1234', 'requirements.txt', level,
                                   package='example', version='1')
                    for level in ('unknown', 'low', 'critical')]
        for order in itertools.permutations(findings):
            with self.subTest(order=[f['severity'] for f in order]):
                self.assertEqual(reports.deduplicate(order)[0]['severity'], 'unknown')

    def test_osv_keeps_the_highest_label_or_score(self):
        members = [{'database_specific': {'severity': 'MODERATE'}}]
        self.assertEqual(osv_scanner.level(members, '9.8'), 'CRITICAL')
        self.assertEqual(osv_scanner.level([{'database_specific': {'severity': 'HIGH'}}], '4.0'), 'HIGH')
        for score in ('NaN', 'inf', '-1', '11', None):
            with self.subTest(score=score):
                self.assertIsNone(osv_scanner.level([], score))


class ProbeTests(unittest.TestCase):
    def test_container_temporary_directory_supports_unprivileged_image_scanners(self):
        args = scanning.container('docker', 'fixture', None, Path('/work'), False)
        self.assertIn('mode=1777', args[args.index('--tmpfs') + 1].split(','))
        self.assertIn('--read-only', args)
        self.assertIn('--cap-drop=ALL', args)

    def test_probe_preserves_snapshot_and_cleans_temporary_files(self):
        for mode in ('success', 'failure', 'cancel'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory(prefix='dso probe ') as directory:
                work = Path(directory)
                source, cache = work / 'source', work / 'cache'
                source.mkdir()
                cache.mkdir()
                (source / '.dso-sentinel').write_text('a real source file with a finding')
                before = {p.name: p.read_bytes() for p in source.iterdir()}

                def process(args, *a, **kw):
                    if args[1] == 'rm':
                        return 0, ''
                    self.assertEqual((source / '.dso-sentinel').read_bytes(), before['.dso-sentinel'])
                    if mode == 'cancel':
                        raise runtime.Cancelled()
                    index = args.index('-c')
                    command = args[index + 1]
                    for mount, folder in (('/work', work), ('/src', source), ('/cache', cache)):
                        command = command.replace(mount + '/', str(folder) + '/')
                    checked = subprocess.run(['/bin/sh', '-c', command, *args[index + 2:]], capture_output=True)
                    self.assertEqual(checked.returncode, 0, checked.stderr.decode())
                    return (0 if mode == 'success' else 1), ''

                with patch.object(scanning, 'run_process', side_effect=process):
                    if mode == 'cancel':
                        with self.assertRaises(runtime.Cancelled):
                            scanning.probe('docker', source, work, 5, cache=cache)
                    else:
                        error = scanning.probe('docker', source, work, 5, cache=cache)
                        self.assertEqual(error is None, mode == 'success')
                self.assertEqual({p.name: p.read_bytes() for p in source.iterdir()}, before)
                self.assertEqual(list(cache.iterdir()), [])

    def test_doctor_does_not_convert_cancellation_to_daemon_failure(self):
        with patch.object(scanning, 'executable_path', return_value='docker'), \
             patch.object(scanning, 'run_process', side_effect=runtime.Cancelled()):
            with self.assertRaises(runtime.Cancelled):
                scanning.doctor('docker')


class FailureTests(unittest.TestCase):
    def test_scanner_size_and_finding_limits_produce_an_incomplete_report(self):
        def process(args, *a, **kw):
            if args[1:] in (['--version'], ['version']):
                return 0, manifest.plugin('gitleaks')['version']
            data = [{'RuleID': 'test-token', 'File': 'test.txt', 'StartLine': n, 'Secret': 'synthetic'}
                    for n in (1, 2)]
            Path(args[args.index('--report-path') + 1]).write_text(json.dumps(data))
            return 10, ''

        for limit in ('REPORT_LIMIT', 'MAX_FINDINGS'):
            with self.subTest(limit=limit), tempfile.TemporaryDirectory() as directory, \
                 patch.object(scanning, 'executable_path', return_value='/tools/gitleaks'), \
                 patch.object(scanning, 'run_process', side_effect=process), patch.object(runtime, limit, 1):
                report = scanning.scan_repo(directory, ['gitleaks'], project='fixture')
            self.assertFalse(report['complete'])
            self.assertEqual(report['runs'][0]['error_code'], 'report_limit')
            self.assertEqual(report['findings'], [])
            reports.validate_report(report)

    def test_invalid_sast_location_is_rejected_during_normalization(self):
        data = {'results': [{'check_id': 'test-rule', 'path': '/src/app.py', 'start': {'line': 0},
                             'extra': {'severity': 'ERROR'}}], 'errors': []}
        with self.assertRaises(ValueError):
            scanning.normalize('semgrep', data, '/src')

    def test_oversized_report_does_not_replace_the_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            path.write_text('previous report')
            with patch.object(runtime, 'REPORT_LIMIT', 128), self.assertRaises(runtime.ScanError) as raised:
                scanning.write_report(path, {'payload': 'x' * 256})
            self.assertEqual(raised.exception.code, 'report_limit')
            self.assertEqual(path.read_text(), 'previous report')
            self.assertEqual([p.name for p in Path(directory).iterdir()], ['report.json'])

    def test_malformed_grype_locations_do_not_abort_other_plugins(self):
        def process(args, cwd, *a, **kw):
            name = Path(args[0]).name
            if args[1:] == ['version'] or args[1:] == ['--version']:
                return 0, manifest.plugin(name)['version']
            if name == 'grype':
                data = {'matches': [{'vulnerability': {'id': 'CVE-2026-1234'},
                                     'artifact': {'locations': []}}]}
                flag = '--file'
            else:
                data = {'SchemaVersion': 2, 'ArtifactName': args[-1]}
                flag = '--output'
            Path(args[args.index(flag) + 1]).write_text(json.dumps(data))
            return 0, ''

        with tempfile.TemporaryDirectory() as directory, \
             patch.object(scanning, 'executable_path', side_effect=lambda name: '/tools/' + name), \
             patch.object(scanning, 'run_process', side_effect=process):
            report = scanning.scan_repo(directory, ['grype', 'trivy'], profile='audit', project='fixture')
        self.assertFalse(report['complete'])
        self.assertEqual([(r['plugin'], r['status']) for r in report['runs']],
                         [('grype', 'error'), ('trivy', 'complete')])
        self.assertEqual(report['runs'][0]['error_code'], 'report')
        reports.validate_report(report)

    def test_scanner_errors_after_long_stderr_are_not_lost(self):
        # The marker straddles the old 256 KiB boundary.
        script = "import sys; sys.stderr.write('x' * (256 * 1024 - 3) + 'error: unreadable file\\n')"
        with self.assertRaises(runtime.ScanError) as raised:
            runtime.run_process([sys.executable, '-c', script], tempfile.gettempdir(), 5,
                                errors_on=(b'error:',))
        self.assertEqual(raised.exception.code, 'scanner_error')


if __name__ == '__main__':
    unittest.main()
