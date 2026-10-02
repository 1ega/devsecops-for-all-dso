import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class GrypeWrapperTest(unittest.TestCase):
    def run_wrapper(self, code=0, source='dir:fixture', threshold='high'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tool = root / 'grype'
            tool.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > "$TEST_ARGS"\nexit "$TEST_RC"\n')
            tool.chmod(0o755)
            env = dict(os.environ, PATH=str(root)+':'+os.environ['PATH'],
                       TEST_ARGS=str(root/'arguments'), TEST_RC=str(code), GRYPE_FAIL_ON=threshold)
            result = subprocess.run(['bash', str(ROOT/'scanners/grype/scan.sh'),
                                     source, str(root/'reports')], env=env,
                                    capture_output=True, text=True, check=False)
            arguments = (root/'arguments').read_text() if (root/'arguments').exists() else ''
            return result, arguments

    def test_gate_and_tool_errors_preserve_exit_status(self):
        for code in (0, 2, 17):
            result, args = self.run_wrapper(code)
            self.assertEqual(result.returncode, code)
            self.assertIn('--fail-on\nhigh', args)

    def test_report_only_removes_gate(self):
        result, args = self.run_wrapper(threshold='off')
        self.assertEqual(result.returncode, 0)
        self.assertNotIn('--fail-on', args)

    def test_options_cannot_be_targets(self):
        result, args = self.run_wrapper(source='--help')
        self.assertEqual(result.returncode, 64)
        self.assertEqual(args, '')


class TrivyWrapperTest(unittest.TestCase):
    def run_wrapper(self, code=0, report=True, version='0.75.0', mode='config', target='fixture'):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tool = root / 'trivy'
            tool.write_text('''#!/bin/sh
if [ "$1" = --version ]; then printf 'Version: %s\\n' "$TEST_VERSION"; exit 0; fi
while [ "$#" -gt 0 ]; do
  if [ "$1" = --output ]; then shift; destination="$1"; fi
  shift
done
if [ "$TEST_REPORT" = true ]; then printf '{"fixture":true}\\n' > "$destination"; fi
exit "$TEST_RC"
''')
            tool.chmod(0o755)
            env = dict(os.environ, PATH=str(root)+':'+os.environ['PATH'],
                       TEST_RC=str(code), TEST_REPORT=str(report).lower(), TEST_VERSION=version)
            return subprocess.run(['bash', str(ROOT/'scanners/trivy/scan.sh'),
                                   mode, target, str(root/'reports')], env=env,
                                  capture_output=True, text=True, check=False)

    def test_clean_and_findings_are_distinct(self):
        self.assertEqual(self.run_wrapper(0).returncode, 0)
        self.assertEqual(self.run_wrapper(10).returncode, 1)

    def test_execution_error_is_not_a_finding_or_pass(self):
        self.assertEqual(self.run_wrapper(17).returncode, 2)

    def test_missing_report_cannot_pass(self):
        self.assertEqual(self.run_wrapper(0, report=False).returncode, 2)

    def test_wrong_tool_version_is_rejected(self):
        self.assertEqual(self.run_wrapper(version='0.74.0').returncode, 69)

    def test_mutable_image_and_option_target_rejected(self):
        self.assertEqual(self.run_wrapper(mode='image', target='app:latest').returncode, 64)
        self.assertEqual(self.run_wrapper(target='--help').returncode, 64)
