import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/dso'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import console  # noqa: E402
import dso  # noqa: E402
import runtime  # noqa: E402
import scanning  # noqa: E402
from test_scanning import dependency, report  # noqa: E402

CLI = [sys.executable, str(ROOT / 'tools/dso/dso.py')]
VARIABLES = ('DSO_CONFIG', 'DSO_REPORTS_DIR', 'DSO_CACHE_DIR', 'DSO_MAX_REPORT_MB', 'DSO_MAX_FINDINGS')


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.file = Path(self.folder.name) / 'config.json'
        clean = {name: os.environ[name] for name in VARIABLES if name in os.environ}
        patcher = patch.dict(os.environ, {'DSO_CONFIG': str(self.file)}, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in VARIABLES[1:]:
            os.environ.pop(name, None)
        self.addCleanup(lambda: os.environ.update(clean))
        self.addCleanup(runtime.set_limits, runtime.MAX_JSON, 50000)

    def write(self, data, mode=0o600):
        self.file.write_text(json.dumps(data))
        self.file.chmod(mode)

    def test_precedence_default_file_environment_option(self):
        values, sources = config.load()
        self.assertEqual((values['max_report_mb'], sources['max_report_mb']), (20, 'default'))
        self.assertEqual(values['reports_dir'], str(Path('~/.dso/reports').expanduser()))
        self.write({'max_report_mb': 64, 'engine': 'docker', 'reports_dir': '~/scans', 'cache_dir': None})
        values, sources = config.load()
        self.assertEqual((values['max_report_mb'], values['engine'], sources['engine']), (64, 'docker', 'file'))
        self.assertEqual(values['reports_dir'], str(Path('~/scans').expanduser()))
        with patch.dict(os.environ, {'DSO_MAX_REPORT_MB': '128', 'DSO_REPORTS_DIR': self.folder.name}):
            values, sources = config.load({'max_report_mb': 256, 'max_findings': None})
        self.assertEqual((values['max_report_mb'], sources['max_report_mb']), (256, 'option'))
        self.assertEqual((values['reports_dir'], sources['reports_dir']), (self.folder.name, 'environment'))
        self.assertEqual(sources['max_findings'], 'default')

    def test_bad_files_and_values_are_refused_with_the_key_named(self):
        cases = [({'max_report_mb': 10}, 'max_report_mb'), ({'max_report_mb': '64'}, 'max_report_mb'),
                 ({'max_findings': True}, 'max_findings'), ({'engine': 'podman'}, 'engine'),
                 ({'profile': 'image'}, 'profile'), ({'profile': 'missing'}, 'profile'),
                 ({'timeout': 0}, 'timeout'), ({'colour': 1}, 'unknown settings colour'),
                 ({'reports_dir': 'a\nb'}, 'reports_dir')]
        for data, expected in cases:
            self.write(data)
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, expected):
                config.load()
        self.write({'max_report_mb': 64}, mode=0o664)
        with self.assertRaisesRegex(ValueError, 'not writable by others'):
            config.load()
        self.file.unlink()
        self.file.symlink_to(Path(self.folder.name) / 'other.json')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            config.load()
        self.file.unlink()
        self.file.write_text('[]')
        with self.assertRaises(ValueError):
            config.load()
        self.file.unlink()
        with patch.dict(os.environ, {'DSO_MAX_FINDINGS': 'lots'}), self.assertRaisesRegex(ValueError, 'DSO_MAX_FINDINGS'):
            config.load()

    def test_init_writes_a_private_file_that_loads_back(self):
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(dso.main(['config', 'init']), 0)
        self.assertIn(str(self.file), printed.getvalue())
        self.assertEqual(self.file.stat().st_mode & 0o777, 0o600)
        data = json.loads(self.file.read_text())
        self.assertEqual({k: v for k, v in data.items() if k != '_help'}, config.DEFAULTS)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(dso.main(['config', 'init']), 2)
        self.assertEqual(dso.main(['config', 'init', '--force']), 0)
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(dso.main(['config', '--format', 'json']), 0)
        shown = json.loads(printed.getvalue())
        # Every default is now spelled out in the file, so that is where values come from.
        self.assertEqual((shown['settings']['max_report_mb'], shown['sources']['max_report_mb']), (20, 'file'))
        style = console.Style(io.StringIO())
        console.config_table(style, *config.load(), self.file)
        self.assertIn('max_report_mb', style.stream.getvalue())

    def test_limits_apply_to_reports_scans_and_gates(self):
        self.write({'max_report_mb': 20, 'max_findings': 1000})
        with contextlib.redirect_stderr(io.StringIO()):
            # A fresh CLI run picks the file up; a gate with --max-findings below the report's size names the option.
            big = report([dependency(f'CVE-2024-{i:04d}') for i in range(1001)], ['trivy'])
            path = Path(self.folder.name) / 'big.json'
            runtime.set_limits(runtime.MAX_JSON, 50000)
            scanning.write_report(path, big)
            errors = io.StringIO()
            with contextlib.redirect_stderr(errors):
                self.assertEqual(dso.main(['gate', '--input', str(path), '--format', 'json']), 2)
            self.assertIn('--max-findings', errors.getvalue())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(dso.main(['gate', '--input', str(path), '--max-findings', '2000', '--format', 'json']), 1)
            runtime.set_limits(1024, 50000)
            with self.assertRaises(runtime.ScanError) as raised:
                scanning.write_report(Path(self.folder.name) / 'small.json', big)
            self.assertEqual(raised.exception.code, 'report_limit')
            self.assertIn('--max-report-mb', str(raised.exception))
            self.assertFalse((Path(self.folder.name) / 'small.json').exists())

    def test_cli_options_and_environment_round_trip(self):
        result = subprocess.run(CLI + ['config', '--format', 'json'], capture_output=True, text=True,
                                env=dict(os.environ, DSO_MAX_REPORT_MB='48'))
        self.assertEqual(result.returncode, 0, result.stderr)
        shown = json.loads(result.stdout)
        self.assertEqual((shown['settings']['max_report_mb'], shown['sources']['max_report_mb']), (48, 'environment'))
        result = subprocess.run(CLI + ['config'], capture_output=True, text=True, env=dict(os.environ, DSO_MAX_REPORT_MB='7'))
        self.assertEqual(result.returncode, 2)
        self.assertIn('DSO_MAX_REPORT_MB', result.stderr)
        self.write({'engine': 'docker', 'profile': 'ci-blocking', 'reports_dir': self.folder.name})
        argv, _ = dso.expand_scan(['scan', self.folder.name], config.load()[0])
        self.assertIn('--profile', argv)
        self.assertEqual(argv[argv.index('--profile') + 1], 'ci-blocking')
        self.assertTrue(argv[-1].startswith(self.folder.name))
        result = subprocess.run(CLI + ['scan', 'repo', '--help'], capture_output=True, text=True)
        self.assertIn('(default: docker)', result.stdout)


if __name__ == '__main__':
    unittest.main()
