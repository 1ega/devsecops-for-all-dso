import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "tools" / "dso" / "dso.py"
CATALOG = json.loads((ROOT / "baseline" / "controls.json").read_text())


class AssessCommandTest(unittest.TestCase):
    def run_assessment(self, assessment):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assessment.json"
            path.write_text(json.dumps(assessment), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(CLI), "assess", "--input", str(path),
                 "--all", "--format", "json"],
                text=True, capture_output=True, check=False,
            )

    def complete_assessment(self):
        today = date.today().isoformat()
        return {
            "organization": "test",
            "as_of": today,
            "controls": {
                control["id"]: {
                    "status": "implemented",
                    "owner": "test-owner",
                    "reviewed_on": today,
                    "evidence": "private-ticket-123",
                }
                for control in CATALOG["controls"]
            },
        }

    def test_complete_assessment_passes(self):
        result = self.run_assessment(self.complete_assessment())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["assessed"], len(CATALOG["controls"]))

    def test_stale_or_unsupported_claim_fails(self):
        assessment = self.complete_assessment()
        assessment["controls"]["BKP-02"]["reviewed_on"] = (
            date.today() - timedelta(days=181)).isoformat()
        assessment["controls"]["DEV-02"]["evidence"] = ""
        result = self.run_assessment(assessment)
        self.assertEqual(result.returncode, 1)
        gaps = {item["id"]: item["issues"] for item in json.loads(result.stdout)["gaps"]}
        self.assertIn("stale review", gaps["BKP-02"])
        self.assertIn("implemented without evidence", gaps["DEV-02"])

    def test_unknown_control_is_input_error(self):
        assessment = self.complete_assessment()
        assessment["controls"]["FAKE-01"] = {}
        result = self.run_assessment(assessment)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown control IDs", result.stderr)

    def test_old_snapshot_cannot_pass_as_current(self):
        assessment = self.complete_assessment()
        assessment["as_of"] = (date.today() - timedelta(days=8)).isoformat()
        result = self.run_assessment(assessment)
        self.assertEqual(result.returncode, 2)
        self.assertIn("as_of is older than 7 days", result.stderr)

    def test_null_and_nontext_evidence_cannot_pass(self):
        for value in (None, False, [], {}):
            assessment = self.complete_assessment()
            assessment["controls"]["DEV-02"]["evidence"] = value
            result = self.run_assessment(assessment)
            self.assertEqual(result.returncode, 1)
            self.assertIn("implemented without evidence", result.stdout)

    def test_nontext_status_does_not_crash(self):
        assessment = self.complete_assessment()
        assessment["controls"]["DEV-02"]["status"] = []
        result = self.run_assessment(assessment)
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid status", result.stdout)

    def test_compact_iso_date_is_rejected(self):
        assessment = self.complete_assessment()
        assessment["as_of"] = date.today().strftime("%Y%m%d")
        result = self.run_assessment(assessment)
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
