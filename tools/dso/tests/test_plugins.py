import io
import os
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/dso'))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
import manifest  # noqa: E402
import scanning as core  # noqa: E402


def only(findings, **expected):
    [f] = findings
    for key, value in expected.items():
        assert f[key] == value, (key, f[key], value)
    return f


class AdapterTests(unittest.TestCase):
    def test_trufflehog_keeps_only_a_fingerprint(self):
        item = {'SourceMetadata': {'Data': {'Filesystem': {'file': '/src/web/config.ini', 'line': 1}}},
                'DetectorName': 'AWS', 'Raw': 'AKIAEXAMPLEKEYID', 'RawV2': 'AKIAEXAMPLEKEYIDsecretpart',
                'Redacted': 'AKIAEXAMPLEKEYID', 'ExtraData': {'account': '123456789012'}}
        findings = core.normalize('trufflehog', [item, item], '/src')
        only(findings, rule_id='AWS', path='web/config.ini', line=1, severity='high', category='secret', cwe=['CWE-798'])
        self.assertNotIn('AKIAEXAMPLE', json.dumps(findings))
        self.assertNotIn('123456789012', json.dumps(findings))
        rotated = dict(item, RawV2='AKIAEXAMPLEKEYIDother')
        self.assertNotEqual(findings[0]['id'], core.normalize('trufflehog', [rotated], '/src')[0]['id'])

    def test_yara_names_the_kit_rule_file(self):
        data = [{'path': '/src/web/shell.php', 'rules': [
            {'identifier': 'WEBSHELL_PHP_Generic_Eval', 'namespace': 'config/yara/rules/rules/yara/signature-base/yara/gen_webshells.yar'}]}]
        only(core.normalize('yara', data, '/src'), path='web/shell.php', line=0, category='malware',
             rule_id='rules/yara/signature-base/yara/gen_webshells.yar:WEBSHELL_PHP_Generic_Eval')
        data[0]['rules'][0]['namespace'] = '/tmp/attacker.yar'
        with self.assertRaises(ValueError):
            core.normalize('yara', data, '/src')

    def test_grype(self):
        data = {'matches': [{'vulnerability': {'id': 'GHSA-35jh-r3h4-6jhm', 'severity': 'High', 'description': 'private',
                                               'fix': {'state': 'fixed', 'versions': ['4.17.21']},
                                               'cwes': [{'cwe': 'CWE-94'}, {'cwe': '<b>'}]},
                             'artifact': {'name': 'lodash', 'version': '4.17.15', 'locations': [{'path': '/package-lock.json'}]}}]}
        f = only(core.normalize('grype', data, '/src'), path='package-lock.json', package='lodash', installed_version='4.17.15',
                 fixed_version='4.17.21', severity='high', cwe=['CWE-94'])
        self.assertIn('https://github.com/advisories/GHSA-35jh-r3h4-6jhm', f['references'])
        self.assertNotIn('private', json.dumps(f))
        # A GitHub advisory with a CVE among the match's related records is named by the CVE, as Trivy names it.
        data['matches'][0]['relatedVulnerabilities'] = [{'id': 'CVE-2020-8203', 'dataSource': 'nvd'},
                                                        {'id': 'CVE-2019-10744'}, {'id': 'junk'}, 'text']
        f = only(core.normalize('grype', data, '/src'), rule_id='CVE-2019-10744')
        self.assertEqual(f['references'][0], 'https://nvd.nist.gov/vuln/detail/CVE-2019-10744')
        data['matches'][0]['vulnerability']['id'] = 'CVE-2024-0001'
        only(core.normalize('grype', data, '/src'), rule_id='CVE-2024-0001')

    def test_osv_scanner_groups_aliases_and_scores(self):
        advisory = {'id': 'GHSA-x84v-xcm2-53pg', 'database_specific': {'severity': 'MODERATE', 'cwe_ids': ['CWE-522']},
                    'affected': [{'package': {'name': 'requests', 'ecosystem': 'PyPI'},
                                  'ranges': [{'events': [{'introduced': '0'}, {'fixed': '2.20.0'}]}]}]}
        pysec = {'id': 'PYSEC-2018-28', 'affected': [{'package': {'name': 'requests', 'ecosystem': 'PyPI'},
                                                      'ranges': [{'events': [{'fixed': '2.20.0'}]}]}]}
        data = {'results': [{'source': {'path': '/src/requirements.txt', 'type': 'lockfile'}, 'packages': [
            {'package': {'name': 'requests', 'version': '2.19.1', 'ecosystem': 'PyPI'},
             'vulnerabilities': [advisory, pysec],
             'groups': [{'ids': ['GHSA-x84v-xcm2-53pg', 'PYSEC-2018-28'], 'max_severity': '9.8',
                         'aliases': ['CVE-2018-18074', 'GHSA-x84v-xcm2-53pg', 'PYSEC-2018-28']},
                        {'ids': ['PYSEC-2099-1'], 'max_severity': '7.5'}]}]}]}
        by_rule = {f['rule_id']: f for f in core.normalize('osv-scanner', data, '/src')}
        cve, other = by_rule['CVE-2018-18074'], by_rule['PYSEC-2099-1']
        self.assertEqual((cve['rule_id'], cve['severity'], cve['fixed_version'], cve['cwe']),
                         ('CVE-2018-18074', 'critical', '2.20.0', ['CWE-522']))
        self.assertEqual((other['rule_id'], other['severity'], other['fixed_version']), ('PYSEC-2099-1', 'high', ''))
        # Without a CVE the GHSA names the group, whatever sorts first among its IDs.
        data['results'][0]['packages'][0]['groups'] = [{'ids': ['BIT-requests-2099-1', 'PYSEC-2099-2'], 'max_severity': '5',
                                                        'aliases': ['BIT-requests-2099-1', 'GHSA-x84v-xcm2-53pg', 'PYSEC-2099-2']}]
        only(core.normalize('osv-scanner', data, '/src'), rule_id='GHSA-x84v-xcm2-53pg')

    def test_trivy_config_reports_failures_only(self):
        data = {'SchemaVersion': 2, 'ArtifactName': '/src', 'Results': [{'Target': 'Dockerfile', 'Misconfigurations': [
            {'ID': 'DS-0002', 'Severity': 'HIGH', 'Status': 'FAIL', 'CauseMetadata': {'StartLine': 3}, 'Message': 'private'},
            {'ID': 'DS-0001', 'Severity': 'MEDIUM', 'Status': 'PASS'}]}]}
        only(core.normalize('trivy-config', data, '/src'), rule_id='DS-0002', path='Dockerfile', line=3,
             severity='high', category='iac')

    def test_poutine_uses_rule_levels(self):
        data = {'findings': [{'rule_id': 'injection', 'purl': 'pkg:x', 'meta': {
                    'path': '.github/workflows/ci.yml', 'line': 10, 'details': 'private'}}],
                'rules': {'injection': {'level': 'error', 'title': 'Injection'}}}
        only(core.normalize('poutine', data, '/src'), path='.github/workflows/ci.yml', line=10, severity='high', category='cicd')


IMAGE = 'docker.io/library/alpine:3.18.0@sha256:' + '0' * 64


class ImageTests(unittest.TestCase):
    def test_trivy_image_paths_do_not_depend_on_the_image_name(self):
        data = {'SchemaVersion': 2, 'ArtifactName': IMAGE, 'Results': [
            {'Target': IMAGE + ' (alpine 3.18.0)', 'Class': 'os-pkgs', 'Type': 'alpine', 'Vulnerabilities': [
                {'VulnerabilityID': 'CVE-2023-6129', 'PkgName': 'libcrypto3', 'InstalledVersion': '3.1.0-r4',
                 'FixedVersion': '3.1.4-r3', 'Severity': 'MEDIUM'}]},
            {'Target': 'Python', 'Class': 'lang-pkgs', 'Type': 'python-pkg', 'Vulnerabilities': [
                {'VulnerabilityID': 'CVE-2024-1', 'PkgName': 'pip', 'InstalledVersion': '23.0',
                 'PkgPath': 'usr/local/lib/python3.9/site-packages/pip-23.0.dist-info/METADATA', 'Severity': 'HIGH'}]}]}
        found = {f['package']: f for f in core.normalize('trivy-image', data, '/')}
        self.assertEqual(found['libcrypto3']['path'], 'os/alpine')
        self.assertEqual(found['pip']['path'], 'usr/local/lib/python3.9/site-packages/pip-23.0.dist-info/METADATA')

    def test_image_scan_report_and_validation(self):
        def fake_run(args, cwd, timeout, cancel=None, extra_env=None, output_path=None, clear=(), errors_on=()):
            name = Path(args[0]).name
            if '--version' in args or args[1:] == ['version']:
                return 0, manifest.plugin(name)['version']
            self.assertIn(IMAGE if name == 'trivy' else 'registry:' + IMAGE, args)
            output = Path(args[args.index('--output' if name == 'trivy' else '--file') + 1])
            output.write_text(json.dumps({'SchemaVersion': 2, 'ArtifactName': IMAGE} if name == 'trivy' else {'matches': []}))
            return 0, ''
        with patch.object(core.shutil, 'which', side_effect=lambda n, **kw: '/tools/' + n), \
             patch.object(core, 'run_process', side_effect=fake_run):
            report = core.scan_image(IMAGE, project=core.image_project(IMAGE))
        self.assertTrue(report['complete'], report['runs'])
        self.assertEqual((report['project'], report['target'], report['input']),
                         ('docker.io/library/alpine', {'type': 'image'}, {'reference': IMAGE}))
        self.assertEqual(core.gate(report)['exit_code'], 0)
        for bad in ('alpine:latest', '-alpine@sha256:' + '0' * 64, IMAGE + ' --help'):
            with self.assertRaises(ValueError):
                core.scan_image(bad, project='p')
        for mutate in (lambda r: r['input'].update(reference='alpine:latest'),
                       lambda r: r['coverage'].update(exclusions=['x'])):
            tampered = json.loads(json.dumps(report))
            mutate(tampered)
            with self.assertRaises(ValueError):
                core.validate_report(tampered)


class DatabaseTests(unittest.TestCase):
    def test_status_row_and_notice(self):
        import console
        audit = manifest.profile('audit')['plugins']
        with tempfile.TemporaryDirectory() as cache, patch.dict('os.environ', {'DSO_CACHE_DIR': cache}):
            missing = core.database_status(audit)
            self.assertEqual({d['name'] for d in missing if not d['present']},
                             {'Trivy vulnerability DB', 'Grype vulnerability DB', 'OSV databases'})
            self.assertIn('downloads about 565 MB now', console.database_row(missing, 'native'))
            style = console.Style(io.StringIO())
            console.database_notice(style, missing, 'native')
            self.assertIn('This scan first downloads vulnerability databases', style.stream.getvalue())
            Path(cache, 'db').mkdir()
            Path(cache, 'db', 'trivy.db').write_bytes(b'x' * 10)
            trivy = core.database_status(['trivy'])
            self.assertEqual((trivy[0]['present'], trivy[0]['bytes']), (True, 10))
            self.assertTrue(console.database_row(trivy, 'native').startswith('cached'))
            style = console.Style(io.StringIO())
            console.database_notice(style, trivy, 'native')
            self.assertEqual(style.stream.getvalue(), '')
            self.assertIn('downloads about 565 MB now', console.database_row(missing, 'docker'))
            self.assertEqual(core.database_status(['gitleaks', 'semgrep']), [])

    def test_database_entries_are_validated(self):
        data = json.loads(manifest.PATH.read_text())
        for bad in ({'name': 'x'}, dict(data['plugins']['trivy']['database'], path='../escape'),
                    dict(data['plugins']['trivy']['database'], download_mb=0)):
            broken = json.loads(json.dumps(data))
            broken['plugins']['trivy']['database'] = bad
            broken['plugins']['trivy-image']['database'] = bad
            with self.assertRaises(ValueError):
                manifest.validate(broken)


class RunnerTests(unittest.TestCase):
    OUTPUT = {'trufflehog': '{"SourceMetadata": {"Data": {"Filesystem": {"file": "/SRC/a.env", "line": 2}}}, '
                            '"DetectorName": "Slack", "Raw": "xoxb-secret"}\n',
              'yr': ''}

    def fake_run(self, args, cwd, timeout, cancel=None, extra_env=None, output_path=None, clear=(), errors_on=()):
        name = Path(args[0]).name
        if '--version' in args or args[1:] == ['version']:
            spec = next(s for s in manifest.plugins().values() if s['executable'] == name)
            return 0, f'{name} {spec["version"]}'
        self.calls.append((name, output_path, clear, errors_on))
        source = args[-1]
        Path(output_path).write_text(self.OUTPUT[name].replace('/SRC', source))
        return (183 if name == 'trufflehog' else 0), ''

    def test_stdout_plugins_and_tool_environment_are_isolated(self):
        self.calls = []
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(core.shutil, 'which', side_effect=lambda n, **kw: '/tools/' + n), \
             patch.object(core, 'run_process', side_effect=self.fake_run):
            Path(folder, 'a.env').write_text('x')
            result = core.scan_repo(folder, ['trufflehog', 'yara'], project='fixture', profile='audit')
        self.assertTrue(result['complete'], result['runs'])
        self.assertEqual([f['rule_id'] for f in result['findings']], ['Slack'])
        for name, output, clear, errors_on in self.calls:
            self.assertTrue(str(output).endswith('result.json'))
            self.assertTrue({'TRUFFLEHOG_', 'YARA_X_', 'GRYPE_'} <= set(clear))
        self.assertEqual([c[3] for c in self.calls if c[0] == 'yr'], [(b'error:',)])

    def test_imageless_plugin_fails_cleanly_with_docker(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(core.shutil, 'which', side_effect=lambda n, **kw: '/tools/' + n), \
             patch.object(core, 'run_process', return_value=(0, '')):
            result = core.scan_repo(folder, ['yara'], engine='docker', project='fixture', profile='audit')
        self.assertEqual(result['runs'][0]['error_code'], 'no_image')
        core.validate_report(result)


if __name__ == '__main__':
    unittest.main()
