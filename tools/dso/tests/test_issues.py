"""Issues: the same problem reported by several scanners is shown once and accepted once."""
import hashlib
import io
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
import console  # noqa: E402
import manifest  # noqa: E402
import reports  # noqa: E402
import scanning  # noqa: E402
from test_scanning import secret  # noqa: E402

IMAGE = 'docker.io/library/alpine:3.18.0@sha256:' + 'c' * 64


def advisory(plugin, rule='CVE-2024-0001', path='requirements.txt', package='django', version='4.2.0',
             severity='high', fixed='', cwe=()):
    return reports.finding(plugin, rule, path, severity, 0, package, version, fixed, cwe=list(cwe))


def trufflehog(path='app.py', line=2, value='one', rule='AWS'):
    fingerprint = hashlib.sha256(b'dso-secret-v2\0' + rule.encode() + b'\0' + value.encode()).hexdigest()
    return reports.finding('trufflehog', rule, path, 'high', line, fingerprint=fingerprint)


def build(findings, plugins, profile='audit', target='repo'):
    """A valid report for any profile: run exit codes follow the manifest."""
    findings = sorted(findings, key=lambda f: f['id'])
    counts = {n: sum(f['plugin'] == n for f in findings) for n in plugins}
    image = target == 'image'
    return {'schema_version': 3, 'project': 'fixture', 'target': {'type': target},
            'created_at': '2026-10-02T00:00:00+00:00',
            'coverage': {'profile': profile, 'plugins': sorted(plugins),
                         'versions': {n: manifest.plugin(n)['version'] for n in plugins}, 'engine': 'native',
                         'policy_digest': 'a' * 64, 'exclusions': [],
                         'default_exclusions': [] if image else sorted(scanning.EXCLUDED)},
            'input': {'reference': IMAGE} if image else {'files': 1, 'bytes': 1, 'sha256': 'b' * 64},
            'complete': True,
            'runs': [{'plugin': n, 'status': 'complete', 'finding_count': counts[n],
                      'exit_code': manifest.plugin(n)['exit_codes']['findings' if counts[n] else 'clean']}
                     for n in sorted(plugins)],
            'findings': findings}


class IssueTests(unittest.TestCase):
    def test_three_dependency_scanners_describe_one_issue(self):
        found = [advisory('trivy', fixed='4.2.1', cwe=['CWE-79']),
                 advisory('grype', package='Django', severity='critical', fixed='4.2.1', cwe=['CWE-80']),
                 advisory('osv-scanner', severity='medium')]
        [issue] = reports.issues(found)
        self.assertEqual((issue['severity'], issue['plugins'], issue['rules'], issue['paths'], issue['line']),
                         ('critical', ['grype', 'osv-scanner', 'trivy'], ['CVE-2024-0001'], ['requirements.txt'], 0))
        self.assertEqual((issue['package'].lower(), issue['installed_version'], issue['fixed_versions'], issue['cwe']),
                         ('django', '4.2.0', ['4.2.1'], ['CWE-79', 'CWE-80']))
        self.assertEqual(issue['findings'], sorted(f['id'] for f in found))
        self.assertEqual(issue['references'][0], 'https://nvd.nist.gov/vuln/detail/CVE-2024-0001')
        self.assertTrue(all(r.startswith('https://cwe.mitre.org/') for r in issue['references'][1:]))
        self.assertEqual(issue['key'], reports.issue_key(found[0]))
        self.assertEqual(reports.issues(found + [advisory('osv-scanner', severity='unknown')])[0]['severity'], 'unknown')

    def test_another_version_lockfile_or_advisory_is_another_issue(self):
        base = advisory('trivy')
        for other in (advisory('grype', version='4.2.1'), advisory('grype', path='backend/requirements.txt'),
                      advisory('grype', rule='CVE-2024-0002'), advisory('grype', package='djangorestframework')):
            with self.subTest(other=other):
                self.assertEqual(len(reports.issues([base, other])), 2)

    def test_tools_spell_packages_and_versions_differently(self):
        maven = [advisory('trivy', rule='CVE-2021-44228', path='pom.xml', package='org.apache.logging.log4j:log4j-core',
                          version='2.14.1'),
                 advisory('grype', rule='CVE-2021-44228', path='pom.xml', package='log4j-core', version='2.14.1')]
        [issue] = reports.issues(maven)
        self.assertEqual(issue['package'], 'org.apache.logging.log4j:log4j-core')
        go = [advisory('trivy', rule='CVE-2023-0001', path='go.mod', package='golang.org/x/net', version='v0.7.0'),
              advisory('osv-scanner', rule='CVE-2023-0001', path='go.mod', package='golang.org/x/net', version='0.7.0')]
        self.assertEqual(len(reports.issues(go)), 1)
        python = [advisory('trivy', package='zope.interface'), advisory('grype', package='Zope_Interface')]
        self.assertEqual(len(reports.issues(python)), 1)

    def test_image_issues_ignore_tool_specific_package_database_paths(self):
        found = [advisory('trivy-image', rule='CVE-2023-6129', path='os/alpine', package='libcrypto3', version='3.1.0-r4'),
                 advisory('grype-image', rule='CVE-2023-6129', path='lib/apk/db/installed', package='libcrypto3',
                          version='3.1.0-r4')]
        [issue] = reports.issues(found, image=True)
        self.assertEqual(issue['paths'], ['lib/apk/db/installed', 'os/alpine'])
        self.assertEqual(len(reports.issues(found)), 2)

    def test_secrets_on_one_line_are_one_issue_but_keep_both_findings(self):
        found = [secret(path='app.py', line=2), trufflehog(path='app.py', line=2)]
        [issue] = reports.issues(found)
        self.assertEqual((issue['rules'], issue['plugins'], issue['line'], len(issue['findings'])),
                         (['AWS', 'test-token'], ['gitleaks', 'trufflehog'], 2, 2))
        self.assertEqual(len(reports.issues([secret(path='app.py', line=2), trufflehog(path='app.py', line=0)])), 2)
        self.assertEqual(len(reports.issues([secret(path='app.py', line=2), trufflehog(path='app.py', line=3)])), 2)

    def test_other_categories_stay_single_and_issues_rank_by_what_blocks_first(self):
        sast = scanning.normalize('semgrep', {'results': [{'check_id': 'rule', 'path': '/src/a.py', 'start': {'line': 3},
                                                           'extra': {'severity': 'WARNING'}}], 'errors': []}, '/src')
        found = sast + [secret(), advisory('trivy', severity='low'), advisory('grype', rule='CVE-2024-0002', severity='unknown'),
                        advisory('osv-scanner', rule='CVE-2024-0003', severity='critical')]
        issues = reports.issues(found)
        self.assertEqual([i['severity'] for i in issues], ['critical', 'high', 'unknown', 'medium', 'low'])
        self.assertEqual([i['findings'] for i in issues if i['category'] == 'sast'], [[sast[0]['id']]])


class GateAcrossToolsTests(unittest.TestCase):
    def test_a_baseline_accepts_a_dependency_issue_whichever_tool_reports_it(self):
        baseline = build([advisory('trivy')], ['trivy'])
        current = build([advisory('trivy'), advisory('grype', package='Django'), advisory('osv-scanner')],
                        ['grype', 'osv-scanner', 'trivy'])
        result = scanning.gate(current, baseline)
        self.assertEqual((result['exit_code'], result['new_or_escalated'], result['existing'], result['mismatch']),
                         (0, 0, 3, []))
        self.assertIn('coverage.plugins', result['coverage_changes'])
        escalated = build([advisory('trivy'), advisory('grype', severity='critical')], ['grype', 'trivy'])
        result = scanning.gate(escalated, baseline)
        self.assertEqual((result['exit_code'], result['new_or_escalated'], [i['plugins'] for i in result['blocking_issues']]),
                         (1, 1, [['grype']]))
        bumped = build([advisory('trivy'), advisory('grype', version='4.2.1')], ['grype', 'trivy'])
        self.assertEqual(scanning.gate(bumped, baseline)['exit_code'], 1)
        unknown = build([advisory('trivy'), advisory('grype', severity='unknown')], ['grype', 'trivy'])
        self.assertEqual(scanning.gate(unknown, baseline)['exit_code'], 1)

    def test_image_baselines_accept_across_package_database_paths(self):
        trivy = advisory('trivy-image', rule='CVE-2023-6129', path='os/alpine', package='libcrypto3', version='3.1.0-r4')
        grype = advisory('grype-image', rule='CVE-2023-6129', path='lib/apk/db/installed', package='libcrypto3',
                         version='3.1.0-r4')
        baseline = build([trivy], ['trivy-image'], profile='image', target='image')
        current = build([trivy, grype], ['grype-image', 'trivy-image'], profile='image', target='image')
        self.assertEqual(scanning.gate(current, baseline)['exit_code'], 0)

    def test_a_secret_from_another_tool_is_never_accepted_through_the_baseline(self):
        baseline = build([secret()], ['gitleaks'])
        current = build([secret(), trufflehog()], ['gitleaks', 'trufflehog'])
        result = scanning.gate(current, baseline)
        self.assertEqual((result['exit_code'], result['new_or_escalated']), (1, 1))
        self.assertEqual([i['plugins'] for i in result['blocking_issues']], [['trufflehog']])

    def test_blocking_findings_are_grouped_for_people_and_kept_for_machines(self):
        current = build([advisory('trivy'), advisory('grype'), advisory('osv-scanner')], ['grype', 'osv-scanner', 'trivy'])
        result = scanning.gate(current)
        self.assertEqual((len(result['blocking']), len(result['blocking_issues'])), (3, 1))
        self.assertEqual(result['blocking_issues'][0]['findings'], [f['id'] for f in current['findings']])


class RenderingTests(unittest.TestCase):
    def test_summaries_count_issues_and_name_every_tool(self):
        current = build([advisory('trivy'), advisory('grype', severity='critical'), advisory('osv-scanner'), secret()],
                        ['gitleaks', 'grype', 'osv-scanner', 'trivy'])
        stream = io.StringIO()
        style = console.Style(stream)
        console.scan_summary(style, current, Path('/tmp/report.json'), scanning.gate(current))
        shown = stream.getvalue()
        self.assertIn('4 findings · 2 issues after merging tools', shown)
        self.assertIn('2 issues would block', shown)
        self.assertIn('CRITICAL · sca · grype, osv-scanner, trivy', shown)
        self.assertLess(shown.index('CRITICAL · sca'), shown.index('HIGH · secret · gitleaks'))
        stream = io.StringIO()
        console.gate_summary(console.Style(stream), scanning.gate(current), 'high')
        self.assertIn('2 issues block (4 findings across tools)', stream.getvalue())


if __name__ == '__main__':
    unittest.main()
