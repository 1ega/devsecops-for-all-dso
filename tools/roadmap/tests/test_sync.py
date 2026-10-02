import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sync import build, inline, narrative, versioned_index


class RoadmapSyncTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "manuals").mkdir()
        (self.root / "baseline").mkdir()
        self.manual = self.root / "manuals/demo.md"
        self.manual.write_text("# Demo\n\n## What it is for\n\nA tool.\n\nUseful checks.\n\n"
                               "## Use\n\n**Run it**\n\n```bash\ndemo --check\n```\n")
        (self.root / "baseline/controls.json").write_text(json.dumps({"controls": [
            {"id": "GOV-01", "title": "Known owners", "owner_role": "IT owner"}]}))
        self.catalog = {
            "repoBase": "https://github.com/example/repo/tree/main/",
            "manualBase": "https://github.com/example/repo/blob/main/manuals/",
            "areas": [{"id": "company", "stages": ["baseline"]}],
            "phases": [{"id": "program"}],
            "stages": [{"id": "baseline", "phase": "program", "controlIds": ["GOV-01"],
                        "tools": [{"id": "demo", "name": "Demo", "validation": "Reference"}]}],
        }

    def test_new_manual_cannot_be_silently_omitted(self):
        (self.root / "manuals/new.md").write_text("# New tool\n")
        with self.assertRaisesRegex(ValueError, "manual/catalog mismatch"):
            build(self.root, self.catalog)

    def test_baseline_control_cannot_be_silently_omitted(self):
        self.catalog["stages"][0]["controlIds"] = []
        with self.assertRaisesRegex(ValueError, "baseline coverage mismatch"):
            build(self.root, self.catalog)

    def test_commands_and_ci_are_preserved(self):
        ci = 'scan:\n  script:\n    - |\n      curl -H "Authorization: $TOKEN" "$URL"'
        with self.manual.open("a") as handle:
            handle.write("\n## CI example\n\n### GitLab CI\n\n```yaml\n" + ci + "\n```\n")
        output = build(self.root, self.catalog)
        payload = json.loads(output.split("window.ROADMAP = ", 1)[1].removesuffix(";\n"))
        tool = payload["stages"][0]["tools"][0]
        self.assertEqual(tool["run"][0]["code"], "demo --check")
        self.assertEqual(tool["ciExamples"][0], {"label": "GitLab CI", "code": ci})

    def test_manual_edits_change_the_generated_site(self):
        before = build(self.root, self.catalog)
        self.manual.write_text(self.manual.read_text().replace("demo --check", "demo --strict"))
        self.assertNotEqual(before, build(self.root, self.catalog))

    def test_raw_html_and_unsafe_link_schemes_are_not_rendered(self):
        rendered = inline('<img src=x onerror=alert(1)> [run](javascript:alert) `safe`',
                          "https://example.com/manuals/demo.md")
        self.assertNotIn("<img", rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn("<code>safe</code>", rendered)

    def test_unknown_repository_resource_fails(self):
        self.catalog["stages"][0]["resources"] = [{"label": "Missing", "path": "missing.md"}]
        with self.assertRaisesRegex(ValueError, "missing or invalid resource"):
            build(self.root, self.catalog)

    def test_troubleshooting_table_is_rendered_and_escaped(self):
        rendered = narrative('| Symptom | Check |\n| :--- | :--- |\n'
                             '| No alerts | <img src=x> and **logs** |', 'https://example.com/')
        self.assertIn('<th>Symptom</th>', rendered)
        self.assertIn('<td>No alerts</td>', rendered)
        self.assertIn('&lt;img src=x&gt;', rendered)
        self.assertIn('<strong>logs</strong>', rendered)

    def test_usage_guidance_survives_code_extraction(self):
        with self.manual.open('a') as handle:
            handle.write('\nOnly use the scoped account.\n')
        output = build(self.root, self.catalog)
        payload = json.loads(output.split('window.ROADMAP = ', 1)[1].removesuffix(';\n'))
        self.assertIn('Only use the scoped account.', payload['stages'][0]['tools'][0]['runNotes'])

    def test_changed_manual_changes_the_data_url(self):
        public = self.root / 'public'
        public.mkdir()
        index = public / 'index.html'
        index.write_text('<link href="styles.css"><script src="data.js"></script>'
                         '<script src="app.js"></script>')
        (public / 'styles.css').write_text('body { color: green; }')
        (public / 'app.js').write_text('console.log("ready");')
        before = versioned_index(self.root, build(self.root, self.catalog))
        index.write_text(before)
        self.assertEqual(before, versioned_index(self.root, build(self.root, self.catalog)))
        self.manual.write_text(self.manual.read_text().replace('demo --check', 'demo --strict'))
        after = versioned_index(self.root, build(self.root, self.catalog))
        self.assertNotEqual(before, after)
        self.assertEqual(before.split('<script src="data.js', 1)[0],
                         after.split('<script src="data.js', 1)[0])

    def test_missing_asset_reference_fails(self):
        public = self.root / 'public'
        public.mkdir()
        (public / 'index.html').write_text('<script src="app.js"></script>')
        (public / 'styles.css').write_text('')
        (public / 'app.js').write_text('')
        with self.assertRaisesRegex(ValueError, 'must reference data.js exactly once'):
            versioned_index(self.root, 'data')


if __name__ == "__main__":
    unittest.main()
