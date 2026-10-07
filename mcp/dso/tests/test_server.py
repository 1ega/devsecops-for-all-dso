import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('dso_server', ROOT / 'mcp/dso/server.py')
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
scanning = server.scanning


def saved_report():
    return {'schema_version': 3, 'project': 'fixture', 'target': {'type': 'repo'},
            'created_at': '2026-10-02T00:00:00+00:00',
            'coverage': {'profile': scanning.DEFAULT_PROFILE, 'plugins': ['gitleaks'],
                         'versions': {'gitleaks': server.manifest.plugin('gitleaks')['version']}, 'engine': 'native',
                         'policy_digest': 'a' * 64, 'exclusions': [], 'default_exclusions': sorted(scanning.EXCLUDED)},
            'input': {'files': 0, 'bytes': 0, 'sha256': 'b' * 64}, 'complete': True,
            'runs': [{'plugin': 'gitleaks', 'status': 'complete', 'finding_count': 0, 'exit_code': 0}],
            'findings': []}


class BoundaryTests(unittest.TestCase):
    def test_root_traversal_absolute_path_and_symlinks(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            root = Path(folder).resolve()
            self.assertEqual(server.contained_path('.', root, True), root)
            for path in ('..', outside, '../' + Path(outside).name, 'missing'):
                with self.assertRaises(ValueError):
                    server.contained_path(path, root, True)
            (root / 'escape').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                server.contained_path('escape', root, True)

    def test_empty_or_filesystem_root_rejected(self):
        for value in ('', '/', '/nonexistent-dso-root'):
            with self.assertRaises(ValueError):
                server.validate_root(value)


class ProtocolTests(unittest.IsolatedAsyncioTestCase):
    async def call(self, session, name, arguments=None):
        result = await session.call_tool(name, arguments or {})
        return result, (None if result.isError else json.loads(result.content[0].text))

    async def test_stdio_initialize_tools_call_and_error(self):
        with tempfile.TemporaryDirectory() as folder:
            args = [str(ROOT / 'mcp/dso/server.py'), '--root', folder, '--engine', 'native']
            parameters = StdioServerParameters(command=sys.executable, args=args)
            if image := os.environ.get('DSO_TEST_IMAGE'):
                parameters = StdioServerParameters(command='docker', args=[
                    'run', '--rm', '-i', '--init', '--read-only', '--cap-drop=ALL',
                    '--security-opt=no-new-privileges', '--tmpfs', '/tmp:rw,nosuid,nodev,size=2g',
                    '--user', f'{os.getuid()}:{os.getgid()}',
                    '--mount', f'type=bind,src={folder},dst=/workspace,readonly', image])
            (Path(folder) / 'report.json').write_text(json.dumps(saved_report()))
            async with stdio_client(parameters) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    initialized = await session.initialize()
                    self.assertEqual(initialized.serverInfo.name, 'dso')
                    tools = await session.list_tools()
                    self.assertEqual({t.name for t in tools.tools},
                                     {'dso_doctor', 'dso_scan_repo', 'dso_read_report', 'dso_get_findings', 'dso_gate'})
                    for name, arguments in [('dso_scan_repo', {'path': '..', 'project': 'fixture'}),
                                            ('dso_scan_repo', {'path': '.', 'project': 'fixture', 'plugins': ['sh']}),
                                            ('dso_scan_repo', {'path': '.', 'project': 'fixture', 'profile': 'missing'}),
                                            ('dso_scan_repo', {'path': '.'}),
                                            ('dso_scan_repo', {'path': '.', 'project': 'fixture', 'pth': '/etc'}),
                                            ('dso_read_report', {'path': '/etc/hosts'}),
                                            ('dso_gate', {'report_id': 'missing'})]:
                        result, _ = await self.call(session, name, arguments)
                        self.assertTrue(result.isError, (name, arguments))
                        self.assertNotIn(folder, result.content[0].text)
                    result, imported = await self.call(session, 'dso_read_report', {'path': 'report.json'})
                    self.assertFalse(result.isError)
                    self.assertEqual((imported['origin'], imported['total']), ('import', 0))
                    result, _ = await self.call(session, 'dso_get_findings', {'report_id': imported['report_id']})
                    self.assertFalse(result.isError)
                    result, grouped = await self.call(session, 'dso_get_findings',
                                                      {'report_id': imported['report_id'], 'view': 'issues'})
                    self.assertFalse(result.isError)
                    self.assertEqual((grouped['view'], grouped['issues'], grouped['total']), ('issues', [], 0))
                    # Imported reports can be baselines, never the gated current scan.
                    result, _ = await self.call(session, 'dso_gate', {'report_id': imported['report_id']})
                    self.assertTrue(result.isError)
                    if image:
                        result, scanned = await self.call(session, 'dso_scan_repo',
                                                          {'path': '.', 'project': 'fixture', 'plugins': ['gitleaks']})
                        self.assertFalse(result.isError)
                        self.assertTrue(scanned['complete'], scanned)
                        result, gated = await self.call(session, 'dso_gate', {'report_id': scanned['report_id'],
                                                                              'baseline_id': imported['report_id']})
                        self.assertFalse(result.isError)
                        self.assertEqual(gated['exit_code'], 0, gated)


if __name__ == '__main__':
    unittest.main()
