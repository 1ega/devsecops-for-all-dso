import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]

try:
    import yaml  # noqa: F401  (check_repo needs PyYAML from tools/validation/requirements.txt)
except ImportError:
    yaml = None


@unittest.skipIf(yaml is None, 'PyYAML is not installed')
class PinDriftTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('check_repo', ROOT / 'tools/validation/check_repo.py')
        self.check = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.check)

    def errors(self, files):
        self.check.text_files = lambda root, imported: iter(files)
        return [e for e in self.check.dso_errors(ROOT, set()) if e.startswith(tuple(name for name, _ in files))]

    def test_every_copy_of_a_pin_must_match_the_manifest(self):
        image = self.check.manifest.plugin('gitleaks')['image']
        drift = [('a.yml', 'image: aquasec/trivy:0.74.0@sha256:' + 'a' * 64),
                 ('b.md', 'docker pull ' + image.split('@')[0]),
                 ('c.md', 'https://github.com/gitleaks/gitleaks/releases/download/v8.29.0/x.tgz'),
                 ('d.txt', 'semgrep==1.170.0'),
                 ('e.yaml', '- repo: https://github.com/gitleaks/gitleaks\n  rev: v8.18.0'),
                 ('f', 'git clone --branch v8.1.0 https://github.com/gitleaks/gitleaks /src'),
                 ('rules/x/run.sh', 'python3 tools/dso/dso.py scan repo .')]
        self.assertEqual(sorted(e.split(':')[0] for e in self.errors(drift)), [name for name, _ in drift])
        self.assertEqual(self.errors([('ok.md', 'docker pull ' + image), ('ok.txt', 'semgrep==1.179.0')]), [])


if __name__ == '__main__':
    unittest.main()
