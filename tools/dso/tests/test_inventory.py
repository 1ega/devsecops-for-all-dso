import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CLI = ROOT / "tools" / "dso" / "dso.py"
FIELDS = ["asset_id", "asset_type", "name", "environment", "owner",
          "criticality", "internet_exposed", "data_classification"]
VALID = ["asset-1", "service", "API", "production", "api-team", "high",
         "true", "confidential"]


class InventoryCommandTest(unittest.TestCase):
    def run_inventory(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "assets.csv"
            with path.open("w", newline="", encoding="utf-8") as target:
                writer = csv.writer(target)
                writer.writerow(FIELDS)
                writer.writerows(rows)
            return subprocess.run(
                [sys.executable, str(CLI), "inventory", "--input", str(path)],
                text=True, capture_output=True, check=False,
            )

    def test_valid_inventory_passes(self):
        result = self.run_inventory([VALID])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_and_missing_owner_fail(self):
        second = VALID.copy()
        second[4] = ""
        result = self.run_inventory([VALID, second])
        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate asset_id", result.stdout)
        self.assertIn("missing owner", result.stdout)

    def test_extra_columns_fail(self):
        result = self.run_inventory([VALID + ["unexpected"]])
        self.assertEqual(result.returncode, 1)
        self.assertIn("extra columns", result.stdout)


if __name__ == "__main__":
    unittest.main()
