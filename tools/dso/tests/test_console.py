import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/dso'))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import console  # noqa: E402
import dso  # noqa: E402
import scanning  # noqa: E402
from test_scanning import dependency, report, secret  # noqa: E402

CLI = [sys.executable, str(ROOT / 'tools/dso/dso.py')]


class Terminal(io.StringIO):
    encoding = 'utf-8'

    def isatty(self):
        return True


def answers(*values):
    pending = list(values)
    return lambda prompt: pending.pop(0)


class CommandLineTests(unittest.TestCase):
    def test_help_version_and_no_arguments_without_a_terminal(self):
        result = subprocess.run(CLI + ['--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        for text in ('interactive menu', 'examples:', 'exit codes:', 'scan', 'gate', 'doctor'):
            self.assertIn(text, result.stdout)
        result = subprocess.run(CLI + ['scan', 'repo', '--help'], capture_output=True, text=True)
        self.assertIn('stable project ID', result.stdout)
        result = subprocess.run(CLI + ['--version'], capture_output=True, text=True)
        self.assertIn(f'dso {scanning.VERSION} (gitleaks', result.stdout)
        result = subprocess.run(CLI, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('\x1b', result.stdout + result.stderr)

    def test_terminal_output_is_text_and_pipes_stay_json(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.json'
            fixture = report([secret(), dependency(fixed='2.0')], ['gitleaks', 'trivy'])
            argv = ['scan', 'repo', folder, '--project', 'fixture', '--output', str(output)]
            with patch.object(scanning, 'scan_repo', return_value=fixture), \
                 contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(dso.main(argv + ['--format', 'text']), 0)
            text = printed.getvalue()
            for value in ('SCAN SESSION', 'COMPLETE · 2 findings', 'BLOCKED at high', 'test-token',
                          'requirements.txt  pkg 1 -> 2.0', 'playbooks/leaked-secret.md'):
                self.assertIn(value, text)
            with patch.object(scanning, 'scan_repo', return_value=fixture), \
                 contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(dso.main(argv), 0)
            self.assertTrue(printed.getvalue().startswith('{"complete": true'))


class MenuTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        patcher = patch.dict(os.environ, {'DSO_REPORTS_DIR': self.folder.name})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_scan_is_the_default_and_asks_one_question(self):
        style = console.Style(io.StringIO())
        argv = console.menu(style, answers('9', '', self.folder.name))
        self.assertEqual(argv, ['scan', str(Path(self.folder.name).resolve())])
        shown = style.stream.getvalue()
        for text in ('Choose 1-8 or q.', 'Detected: local folder', 'Running: dso scan'):
            self.assertIn(text, shown)
        self.assertNotIn('\x1b', shown)

    def test_gate_defaults_to_the_latest_report_and_quit_returns_none(self):
        latest = Path(self.folder.name) / 'app.json'
        latest.write_text('{}')
        argv = console.menu(console.Style(io.StringIO()), answers('2', '', '', ''))
        self.assertEqual(argv, ['gate', '--input', str(latest)])
        self.assertIsNone(console.menu(console.Style(io.StringIO()), answers('q')))

    def test_q_at_a_question_goes_back_to_the_command_list(self):
        style = console.Style(io.StringIO())
        self.assertIsNone(console.menu(style, answers('1', 'q', '2', 'Q', 'q')))
        self.assertEqual(style.stream.getvalue().count('Back to the command list.'), 2)

    def test_missing_paths_are_asked_again(self):
        style = console.Style(io.StringIO())
        argv = console.menu(style, answers('5', '/nonexistent/assessment.json', str(Path(__file__))))
        self.assertEqual(argv, ['assess', '--input', str(Path(__file__))])
        self.assertIn('No such file.', style.stream.getvalue())


class RenderingTests(unittest.TestCase):
    def test_untrusted_text_cannot_drive_the_terminal(self):
        self.assertEqual(console.safe('a\x1b[31m\x9b2J‮b'), 'a\\x1b[31m\\x9b2J\\u202eb')
        f = secret(path='evil‮.py')
        stream = Terminal()
        console.card(console.Style(stream), f)
        self.assertIn('evil\\u202e.py', stream.getvalue())

    def test_colour_only_on_a_terminal_and_never_with_no_color(self):
        with patch.dict(os.environ, {'NO_COLOR': ''}):
            stream = Terminal()
            console.banner(console.Style(stream))
            self.assertIn('\x1b[', stream.getvalue())
            self.assertIn('█', stream.getvalue())
        with patch.dict(os.environ, {'NO_COLOR': '1'}):
            stream = Terminal()
            console.banner(console.Style(stream))
            self.assertNotIn('\x1b[', stream.getvalue())

    def test_gate_and_progress_rendering(self):
        stream = io.StringIO()
        style = console.Style(stream)
        current = report([secret()])
        console.gate_summary(style, scanning.gate(current, current), 'high')
        self.assertIn('PASSED at high', stream.getvalue())
        view = console.ScanView(style, None)
        view.progress('start', 'gitleaks')
        view.progress('done', 'gitleaks', {'plugin': 'gitleaks', 'status': 'error', 'finding_count': 0,
                                           'exit_code': 2, 'error_code': 'execution', 'error': 'failed'})
        self.assertIn('01 x gitleaks     FAILED    execution', stream.getvalue())


if __name__ == '__main__':
    unittest.main()
