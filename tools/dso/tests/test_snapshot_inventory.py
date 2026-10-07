"""The snapshot inventory: what was there to scan, and which plugins had nothing to check."""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
import console  # noqa: E402
import inventory  # noqa: E402
import reports  # noqa: E402
import scanning  # noqa: E402
from test_issues import build  # noqa: E402
from test_scanning import secret  # noqa: E402

TREE = {'app/main.py': 'print(1)\n', 'app/util.py': '', 'web/index.ts': '', 'web/package.json': '{}',
        'web/package-lock.json': '{}', 'api/package.json': '{}', 'app/requirements.txt': 'requests==2.19.1\n',
        'app/requirements-dev.txt': '', 'go.mod': 'module x\n', 'svc/pyproject.toml': '', 'svc/poetry.lock': '',
        'lib/pyproject.toml': '', 'Dockerfile': 'FROM scratch\n', 'infra/main.tf': '', 'infra/vars.tfvars': '',
        'k8s/deploy.yaml': 'apiVersion: apps/v1\nkind: Deployment\n', 'k8s/values.yaml': 'replicas: 1\n',
        'chart/Chart.yaml': 'name: x\n', 'compose.yaml': 'services: {}\n',
        'cfn/stack.json': '{"AWSTemplateFormatVersion": "2010-09-09"}',
        '.github/workflows/ci.yml': 'on: push\n', '.github/workflows/notes.md': '', '.gitlab-ci.yml': '',
        'ci/azure-pipelines.yml': '', '.tekton/run.yaml': '', 'README.md': '', '.semgrepignore': ''}


def tree(root):
    for rel, body in TREE.items():
        path = Path(root) / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)


class InventoryTests(unittest.TestCase):
    def test_classifies_languages_lockfiles_manifests_iac_and_ci(self):
        with tempfile.TemporaryDirectory() as root:
            tree(root)
            stock = inventory.collect(root)
        self.assertEqual(stock['languages'], {'python': 2, 'typescript': 1})
        self.assertEqual(stock['dependency_files'], {'go': ['go.mod'], 'npm': ['web/package-lock.json'],
                                                     'pip': ['app/requirements-dev.txt', 'app/requirements.txt', 'svc/poetry.lock']})
        self.assertEqual(stock['unlocked'], {'npm': ['api/package.json'], 'pip': ['lib/pyproject.toml']})
        self.assertEqual(stock['iac_files'], {'cloudformation': 1, 'compose': 1, 'dockerfile': 1, 'helm': 1,
                                              'kubernetes': 1, 'terraform': 2})
        self.assertEqual(stock['ci_files'], {'azure-pipelines': 1, 'github-actions': 1, 'gitlab-ci': 1, 'tekton': 1})
        self.assertEqual(stock, json.loads(json.dumps(stock)))
        inventory.check(stock, len(TREE), reports.relative_path)
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(inventory.collect(root), {'languages': {}, 'dependency_files': {}, 'unlocked': {},
                                                       'iac_files': {}, 'ci_files': {}})

    def test_stored_inventories_are_validated(self):
        with tempfile.TemporaryDirectory() as root:
            tree(root)
            stock = inventory.collect(root)
        report = build([secret()], ['gitleaks', 'trivy'], profile='ci-blocking')
        report['input']['files'] = len(TREE)
        report['input']['inventory'] = stock
        reports.validate_report(report)
        for mutate in (lambda s: s['languages'].update(cobol=1), lambda s: s['languages'].update(python=0),
                       lambda s: s['iac_files'].update(dockerfile=len(TREE) + 1), lambda s: s['ci_files'].update(jenkins=1),
                       lambda s: s['dependency_files'].update(pip=['../x']), lambda s: s['dependency_files'].update(pip=[]),
                       lambda s: s['dependency_files'].update(pip=['b', 'a']), lambda s: s['unlocked'].update(cargo=['/abs']),
                       lambda s: s.pop('ci_files'), lambda s: s.update(extra=1)):
            tampered = json.loads(json.dumps(report))
            mutate(tampered['input']['inventory'])
            with self.subTest(mutate=mutate), self.assertRaises(ValueError):
                reports.validate_report(tampered)
        # Reports written before the inventory existed still load; they simply report no gaps.
        del report['input']['inventory']
        reports.validate_report(report)
        self.assertEqual(reports.gaps(report), [])

    def test_gaps_name_the_plugins_that_had_nothing_to_check(self):
        report = build([], ['gitleaks', 'grype', 'osv-scanner', 'poutine', 'semgrep', 'trivy', 'trivy-config'])
        report['input']['inventory'] = {'languages': {}, 'dependency_files': {}, 'unlocked': {'npm': ['package.json']},
                                        'iac_files': {}, 'ci_files': {}}
        gaps = {g['reason']: g for g in reports.gaps(report)}
        self.assertEqual(set(gaps), {'no_dependency_files', 'unlocked_manifests', 'no_iac_files', 'no_ci_files', 'no_source_files'})
        self.assertEqual(gaps['no_dependency_files']['plugins'], ['grype', 'osv-scanner', 'trivy'])
        self.assertEqual((gaps['unlocked_manifests']['paths'], gaps['no_ci_files']['plugins'], gaps['no_source_files']['plugins']),
                         (['package.json'], ['poutine'], ['semgrep']))
        self.assertEqual(scanning.gate(report)['gaps'], reports.gaps(report))
        report['input']['inventory'].update(languages={'python': 1}, dependency_files={'pip': ['requirements.txt']},
                                            unlocked={}, iac_files={'dockerfile': 1}, ci_files={'github-actions': 1})
        self.assertEqual(reports.gaps(report), [])
        secrets_only = build([], ['gitleaks'])
        secrets_only['input']['inventory'] = {'languages': {}, 'dependency_files': {}, 'unlocked': {}, 'iac_files': {}, 'ci_files': {}}
        self.assertEqual(reports.gaps(secrets_only), [])

    def test_scan_records_the_inventory_and_the_terminal_shows_it(self):
        def process(args, *a, **kw):
            if args[1:] == ['version']:
                return 0, scanning.manifest.plugin('gitleaks')['version']
            Path(args[args.index('--report-path') + 1]).write_text('[]')
            return 0, ''
        with tempfile.TemporaryDirectory() as root:
            tree(root)
            with patch.object(scanning, 'executable_path', return_value='/tools/gitleaks'), \
                 patch.object(scanning, 'run_process', side_effect=process):
                stream = io.StringIO()
                view = console.ScanView(console.Style(stream), None)
                report = scanning.scan_repo(root, ['gitleaks'], project='fixture', progress=view.progress)
        self.assertTrue(report['complete'], report['runs'])
        self.assertEqual(report['input']['inventory']['languages'], {'python': 2, 'typescript': 1})
        reports.validate_report(report)
        shown = stream.getvalue()
        self.assertIn('python 2 · typescript 1 · go: go.mod · npm: web/package-lock.json', shown)
        self.assertIn('dockerfile 1', shown)
        stream = io.StringIO()
        gated = build([], ['grype', 'trivy'])
        gated['input']['inventory'] = {'languages': {}, 'dependency_files': {}, 'unlocked': {'npm': ['a/package.json', 'b/package.json']},
                                       'iac_files': {}, 'ci_files': {}}
        console.gate_summary(console.Style(stream), scanning.gate(gated), 'high')
        self.assertIn('grype, trivy: no lockfile in the snapshot, so dependencies were not checked', stream.getvalue())
        self.assertIn('skipped by the dependency scanners: a/package.json, b/package.json', stream.getvalue())


if __name__ == '__main__':
    unittest.main()
