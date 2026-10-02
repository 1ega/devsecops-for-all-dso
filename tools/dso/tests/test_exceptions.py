import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

CLI = Path(__file__).resolve().parents[3] / "tools" / "dso" / "dso.py"


class ExceptionTest(unittest.TestCase):
    def entry(self):
        return dict(id="EX-1", tool="falco", rule_id="runtime.local.web-shell",
                    asset_id="api-prod", owner="platform", approver="risk-owner",
                    reason="Approved test", compensating_control="Access reviewed",
                    ticket="private-123", created_on=date.today().isoformat(),
                    expires_on=(date.today() + timedelta(days=7)).isoformat())

    def run_register(self, entries):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "exceptions.json"
            source.write_text(json.dumps({"exceptions": entries}))
            return subprocess.run([sys.executable, str(CLI), "exceptions", "--input",
                                   str(source), "--format", "json"], capture_output=True,
                                  text=True, check=False)

    def test_valid_and_empty_register(self):
        for entries in ([], [self.entry()]):
            self.assertEqual(self.run_register(entries).returncode, 0)

    def test_expired_unowned_and_duplicate_fail(self):
        entry = self.entry()
        entry["owner"] = None
        entry["expires_on"] = date.today().isoformat()
        result = self.run_register([entry, entry])
        self.assertEqual(result.returncode, 1)
        issues = " ".join(json.loads(result.stdout)["issues"])
        for expected in ("expired", "missing owner", "duplicate id"):
            self.assertIn(expected, issues)

    def test_indefinite_exception_fails(self):
        entry = self.entry()
        entry["expires_on"] = (date.today() + timedelta(days=91)).isoformat()
        self.assertEqual(self.run_register([entry]).returncode, 1)

    def test_malformed_entry_is_input_error(self):
        result = self.run_register([None])
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
