"""Exceptions: time-boxed, owned waivers applied to a gate, and the triage that records them."""
import contextlib
import io
import json
import os
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
import console  # noqa: E402
import dso  # noqa: E402
import register  # noqa: E402
import scanning  # noqa: E402
from test_console import answers  # noqa: E402
from test_issues import advisory, build, trufflehog  # noqa: E402
from test_scanning import secret  # noqa: E402

TODAY = date.today()


def entry(**overrides):
    base = dict(id='EXC-1', tool='trivy', rule_id='CVE-2024-0001', asset_id='fixture', owner='platform', approver='risk',
                reason='Not reachable from the request path', compensating_control='WAF rule 12', ticket='SEC-1',
                created_on=(TODAY - timedelta(days=6)).isoformat(), expires_on=(TODAY + timedelta(days=24)).isoformat())
    base.update(overrides)
    return base


def mixed():
    """Three tools on one dependency issue, plus a secret."""
    return build([advisory('trivy'), advisory('grype', severity='critical'), advisory('osv-scanner', severity='unknown'),
                  secret()], ['gitleaks', 'grype', 'osv-scanner', 'trivy'])


class RegisterTests(unittest.TestCase):
    def test_problems_distinguish_structure_from_expiry(self):
        self.assertEqual(register.problems({'exceptions': [entry()]}), [])
        self.assertEqual(register.problems({'exceptions': [entry(expires_on=TODAY.isoformat())]}),
                         [('expired', 'exception 1: expired')])
        for broken, expected in ((entry(owner=''), 'missing owner'), (entry(approver='Platform'), 'must differ'),
                                 (entry(reason='a\x1bb'), 'control characters'), (entry(created_on='next week'), 'YYYY-MM-DD'),
                                 (entry(created_on=(TODAY + timedelta(days=1)).isoformat()), 'future'),
                                 (entry(expires_on=(TODAY + timedelta(days=91)).isoformat()), '1–90 days')):
            with self.subTest(expected=expected):
                found = register.problems({'exceptions': [broken]})
                self.assertEqual([kind for kind, _ in found], ['structure'])
                self.assertIn(expected, found[0][1])
        found = register.problems({'exceptions': [entry(), entry(id='exc-1'), entry(id='EXC-2')]})
        self.assertEqual([m for _, m in found], ['exception 2: duplicate id exc-1', 'exception 2: duplicate exception scope',
                                                 'exception 3: duplicate exception scope'])
        for malformed in ({'exceptions': {}}, [], {'exceptions': [None]}):
            with self.assertRaises(ValueError):
                register.problems(malformed)

    def test_load_refuses_a_broken_register_but_keeps_expired_entries(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'exceptions.json'
            path.write_text(json.dumps({'exceptions': [entry(), entry(id='EXC-2', rule_id='CVE-2024-0002',
                                                                        expires_on=TODAY.isoformat())]}))
            self.assertEqual([e['id'] for e in register.load(path)], ['EXC-1', 'EXC-2'])
            path.write_text(json.dumps({'exceptions': [entry(approver='platform')]}))
            with self.assertRaisesRegex(ValueError, 'register rejected: exception 1: owner and approver must differ'):
                register.load(path)
            self.assertEqual(register.read(Path(folder) / 'missing.json'), [])
            written = register.write(Path(folder) / 'new' / 'exceptions.json', [entry()])
            self.assertEqual(written.stat().st_mode & 0o777, 0o600)
            self.assertEqual(register.read(written), [entry()])
            self.assertEqual(register.next_id([entry(id=f'EXC-{TODAY:%Y%m%d}-1')], TODAY), f'EXC-{TODAY:%Y%m%d}-2')


class GateWithExceptionsTests(unittest.TestCase):
    def test_an_active_entry_waives_the_whole_dependency_issue(self):
        report = mixed()
        result = scanning.gate(report, exceptions=[entry()])
        self.assertEqual((result['status'], len(result['blocking']), result['exceptions']['waived']), ('blocked', 1, 3))
        self.assertEqual(result['blocking'][0]['plugin'], 'gitleaks')
        self.assertEqual(len(result['exceptions']['applied'][0]['findings']), 3)
        self.assertEqual((result['exceptions']['expired'], result['exceptions']['unused']), ([], []))
        passed = scanning.gate(report, exceptions=[entry(), entry(id='EXC-2', tool='gitleaks', rule_id='test-token')])
        self.assertEqual((passed['exit_code'], passed['status'], passed['exceptions']['waived']), (0, 'passed', 4))
        self.assertIsNone(scanning.gate(report)['exceptions'])

    def test_expired_unused_and_foreign_entries_waive_nothing(self):
        report = mixed()
        lapsed = entry(expires_on=TODAY.isoformat())
        result = scanning.gate(report, exceptions=[lapsed, entry(id='EXC-2', rule_id='CVE-2099-1'),
                                                   entry(id='EXC-3', asset_id='other-project'),
                                                   entry(id='EXC-4', tool='semgrep')])
        self.assertEqual((result['exit_code'], len(result['blocking']), result['exceptions']['waived']), (1, 4, 0))
        self.assertEqual([e['id'] for e in result['exceptions']['expired']], ['EXC-1'])
        self.assertEqual(result['exceptions']['unused'], ['EXC-2', 'EXC-3', 'EXC-4'])
        wide = scanning.gate(report, exceptions=[entry(tool='*', asset_id='FIXTURE')])
        self.assertEqual(wide['exceptions']['waived'], 3)

    def test_a_secret_exception_covers_only_its_own_finding(self):
        report = build([secret(), trufflehog()], ['gitleaks', 'trufflehog'])
        result = scanning.gate(report, exceptions=[entry(tool='gitleaks', rule_id='test-token')])
        self.assertEqual([f['plugin'] for f in result['blocking']], ['trufflehog'])

    def test_cli_applies_a_register_and_refuses_a_broken_one(self):
        with tempfile.TemporaryDirectory() as folder:
            report, exceptions = Path(folder) / 'report.json', Path(folder) / 'exceptions.json'
            scanning.write_report(report, mixed())
            register.write(exceptions, [entry(), entry(id='EXC-2', tool='gitleaks', rule_id='test-token',
                                                        expires_on=(TODAY + timedelta(days=3)).isoformat())])
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(dso.main(['gate', '--input', str(report), '--exceptions', str(exceptions), '--format', 'json']), 0)
            self.assertEqual(json.loads(printed.getvalue())['exceptions']['waived'], 4)
            with contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(dso.main(['gate', '--input', str(report), '--exceptions', str(exceptions), '--format', 'text']), 0)
            self.assertIn('exception EXC-1 waives 3 findings until', printed.getvalue())
            self.assertIn('exception EXC-2 waives 1 finding until', printed.getvalue())
            self.assertIn('4 waived by exceptions', printed.getvalue())
            register.write(exceptions, [entry(approver='platform')])
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(dso.main(['gate', '--input', str(report), '--exceptions', str(exceptions)]), 2)
            self.assertIn('register rejected', errors.getvalue())


class TriageTests(unittest.TestCase):
    def test_triage_records_one_entry_per_tool_and_rule_then_the_gate_passes(self):
        # Critical ranks first, so the dependency issue is offered before the high secret.
        report = build([advisory('trivy'), advisory('grype', severity='critical'), advisory('osv-scanner'), secret()],
                       ['gitleaks', 'grype', 'osv-scanner', 'trivy'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'exceptions.json'
            style = console.Style(io.StringIO())
            # Accept the dependency issue (approver first equal to the owner, then corrected), stop at the secret.
            ask = answers('a', 'platform', 'platform', 'risk', 'Not reachable', 'WAF rule 12', 'SEC-1', '45', 'q')
            added = console.triage(style, ask, report, [], path, today=TODAY)
            shown = style.stream.getvalue()
            # One advisory seen by three tools is one decision: a single entry for any tool.
            self.assertEqual(added, 1)
            self.assertIn('Owner and approver must differ.', shown)
            self.assertIn('Issue 1 of 2', shown)
            entries = register.read(path)
            self.assertEqual([(e['tool'], e['rule_id'], e['asset_id']) for e in entries], [('*', 'CVE-2024-0001', 'fixture')])
            self.assertEqual((entries[0]['owner'], entries[0]['approver'], entries[0]['id']),
                             ('platform', 'risk', f'EXC-{TODAY:%Y%m%d}-1'))
            self.assertEqual(entries[0]['expires_on'], (TODAY + timedelta(days=45)).isoformat())
            self.assertEqual(register.problems({'exceptions': entries}), [])
            result = scanning.gate(report, exceptions=entries)
            self.assertEqual([f['plugin'] for f in result['blocking']], ['gitleaks'])
            self.assertEqual(result['exceptions']['waived'], 3)
            # A second pass offers only the secret; accepting it writes an entry for its one tool and rule.
            style = console.Style(io.StringIO())
            ask = answers('a', 'platform', 'risk', 'Test fixture', 'Not a live credential', 'SEC-2', '7')
            self.assertEqual(console.triage(style, ask, report, entries, path, today=TODAY), 1)
            self.assertIn('1 blocking issue in fixture · 1 exception in the register', style.stream.getvalue())
            entries = register.read(path)
            self.assertEqual([(e['tool'], e['rule_id']) for e in entries], [('*', 'CVE-2024-0001'), ('gitleaks', 'test-token')])
            self.assertEqual(scanning.gate(report, exceptions=entries)['exit_code'], 0)
            # Nothing left to triage: skipping is a no-op and the file stays as it is.
            self.assertEqual(console.triage(console.Style(io.StringIO()), answers('s'), report, entries, path, today=TODAY), 0)
            self.assertEqual(len(register.read(path)), 2)
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(dso.main(['triage', '--input', str(path), '--exceptions', str(path)]), 2)
            self.assertIn('run it in a terminal', errors.getvalue())


if __name__ == '__main__':
    unittest.main()
