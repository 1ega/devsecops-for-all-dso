import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools/dso'))
os.environ['DSO_CONFIG'] = os.path.join(tempfile.gettempdir(), 'dso-tests-no-config.json')
sys.path.insert(0, str(Path(__file__).resolve().parent))
import console  # noqa: E402
import dso  # noqa: E402
import runtime  # noqa: E402
import scanning  # noqa: E402
import sources  # noqa: E402
from test_scanning import report, secret  # noqa: E402

GIT = shutil.which('git')
COMMIT = 'a' * 40


def git(repo, *args, data=None):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
    return subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-C', str(repo), *args],
                          input=data, capture_output=True, check=True, env=env).stdout.decode().strip()


def make_repository(folder, entries):
    """A repository built from plumbing, so it can hold trees a checkout could not produce."""
    repo = Path(folder) / 'origin'
    subprocess.run(['git', 'init', '-q', '-b', 'main', str(repo)], check=True, capture_output=True)
    for mode, path, content in entries:
        oid = COMMIT if mode == '160000' else git(repo, 'hash-object', '-w', '--stdin', data=content)
        git(repo, 'update-index', '--add', '--cacheinfo', f'{mode},{oid},{path}')
    commit = git(repo, 'commit-tree', git(repo, 'write-tree'), '-m', 'fixture')
    git(repo, 'update-ref', 'refs/heads/main', commit)
    return repo, commit


@contextlib.contextmanager
def local_github(repo):
    allowed = [c.replace('protocol.allow=never', 'protocol.allow=always') for c in sources.GIT_CONFIG]
    data = {'name': 'repo', 'private': False, 'archived': False, 'fork': False, 'size': 1, 'owner': {'login': 'owner'}}
    with patch.object(sources, 'GIT_CONFIG', allowed), patch.object(sources, 'repository', return_value=data), \
         patch.object(sources, 'clone_url', return_value=repo.as_uri()):
        yield


class ParseTests(unittest.TestCase):
    def test_github_urls(self):
        for value, expected in [('https://github.com/octocat/Hello-World', ('octocat', 'Hello-World')),
                                ('https://github.com/octocat/Hello-World.git/', ('octocat', 'Hello-World')),
                                ('github.com/octocat/.github', ('octocat', '.github')),
                                ('https://github.com/octocat', ('octocat', None))]:
            self.assertEqual(sources.parse(value), expected)
        for value in ('https://gitlab.com/a/b', 'http://github.com/a/b', 'https://github.com/a/b/tree/main',
                      'https://github.com/-a/b', 'https://github.com/a/..', 'git@github.com:a/b.git'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                sources.parse(value)
        self.assertTrue(sources.is_remote('git@github.com:a/b.git'))
        self.assertFalse(sources.is_remote('./github.com'))

    def test_tree_listing_rules(self):
        def listing(*rows):
            return b''.join(f'{mode} {kind} {oid} {size}\t{path}\0'.encode() for mode, kind, oid, size, path in rows)
        blob = 'b' * 40
        files = sources.tree_entries(listing(('100644', 'blob', blob, '5', 'app.py'),
                                             ('120000', 'blob', blob, '5', 'link'),
                                             ('160000', 'commit', blob, '-', 'vendor/sub'),
                                             ('100644', 'blob', blob, '5', 'node_modules/x.js'),
                                             ('100755', 'blob', blob, '5', 'skip/me.sh')), ['skip'])
        self.assertEqual(files, [('app.py', blob, 5)])
        for path in ('.git/config', 'a/../b', 'a/.GIT/x', 'bad\nname'):
            with self.subTest(path=path), self.assertRaises(runtime.ScanError):
                sources.tree_entries(listing(('100644', 'blob', blob, '5', path)), [])
        with self.assertRaises(runtime.ScanError):
            sources.tree_entries(listing(('100644', 'blob', blob, str(runtime.MAX_FILE + 1), 'big.bin')), [])


@unittest.skipIf(GIT is None, 'git is not installed')
class FetchTests(unittest.TestCase):
    def test_list_metadata_avoids_per_repository_api_request(self):
        with tempfile.TemporaryDirectory() as folder:
            repo, _ = make_repository(folder, [('100644', 'app.py', b'print(1)\n')])
            work = Path(folder) / 'work'
            work.mkdir()
            metadata = {'name': 'repo', 'private': False, 'archived': False, 'fork': False,
                        'size': 1, 'owner': {'login': 'owner'}}
            with local_github(repo), patch.object(sources, 'repository', side_effect=AssertionError('extra API request')):
                tree, _, _ = sources.fetch('owner', 'repo', work, metadata=metadata)
            self.assertEqual((tree / 'app.py').read_text(), 'print(1)\n')

    def test_raw_blobs_without_checkout_side_effects(self):
        with tempfile.TemporaryDirectory() as folder:
            repo, commit = make_repository(folder, [
                ('100644', '.gitattributes', b'* text eol=crlf\nhidden.txt export-ignore\n'),
                ('100644', 'app.py', b'print(1)\n'),
                ('100644', 'hidden.txt', b'token\n'),
                ('120000', 'link', b'/etc/passwd'),
                ('160000', 'sub', b''),
                ('100644', 'node_modules/x.js', b'x\n')])
            work = Path(folder) / 'work'
            work.mkdir()
            with local_github(repo):
                tree, origin, files = sources.fetch('owner', 'repo', work)
            self.assertEqual(origin, {'url': 'https://github.com/owner/repo', 'commit': commit})
            self.assertEqual(sorted(p.relative_to(tree).as_posix() for p in tree.rglob('*')),
                             ['.gitattributes', 'app.py', 'hidden.txt'])
            # Raw content: no eol conversion, and export-ignore cannot hide a file.
            self.assertEqual((tree / 'app.py').read_bytes(), b'print(1)\n')
            self.assertEqual((tree / 'hidden.txt').stat().st_mode & 0o777, 0o600)

    def test_case_collisions_never_drop_a_file(self):
        with tempfile.TemporaryDirectory() as folder:
            repo, _ = make_repository(folder, [('100644', 'Key.txt', b'one\n'), ('100644', 'key.txt', b'two\n')])
            work = Path(folder) / 'work'
            work.mkdir()
            with local_github(repo):
                try:
                    tree, _, _ = sources.fetch('owner', 'repo', work)
                except runtime.ScanError as exc:
                    self.assertEqual(exc.code, 'path_collision')  # case-insensitive filesystem
                else:
                    self.assertEqual({(tree / n).read_text() for n in ('Key.txt', 'key.txt')}, {'one\n', 'two\n'})


class CommandTests(unittest.TestCase):
    def test_repository_url_defaults_the_project_and_records_the_origin(self):
        origin = {'url': 'https://github.com/owner/repo', 'commit': COMMIT}
        with tempfile.TemporaryDirectory() as folder:
            @contextlib.contextmanager
            def checkout(owner, name, exclusions=(), cancel=None, progress=None):
                yield folder, origin
            fixture = report([secret()], project='github.com/owner/repo')
            with patch.object(sources, 'checkout', side_effect=checkout), \
                 patch.object(scanning, 'scan_repo', return_value=fixture) as scan, \
                 contextlib.redirect_stdout(io.StringIO()):
                code = dso.main(['scan', 'repo', 'https://github.com/owner/repo', '--output', f'{folder}/r.json'])
            self.assertEqual(code, 0)
            self.assertEqual(scan.call_args.args[4], 'github.com/owner/repo')
            self.assertEqual(scan.call_args.kwargs['origin'], origin)
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(dso.main(['scan', 'repo', 'https://github.com/owner', '--output', f'{folder}/r.json']), 2)
                self.assertEqual(dso.main(['scan', 'repo', folder, '--output', f'{folder}/r.json']), 2)
            self.assertIn('dso scan org', errors.getvalue())
            self.assertIn('--project is required', errors.getvalue())

    def test_organization_scan_writes_one_report_each_and_a_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            @contextlib.contextmanager
            def checkout(owner, name, exclusions=(), cancel=None, progress=None, metadata=None):
                if name == 'gone':
                    raise runtime.ScanError('not_found', 'Not found on GitHub')
                self.assertEqual(metadata['name'], name)
                yield folder, {'url': f'https://github.com/{owner}/{name}', 'commit': COMMIT}
            skipped = {'fork': 1, 'archived': 0, 'empty': 0, 'over_limit': 0}
            output = Path(folder) / 'out'
            argv = ['scan', 'org', 'https://github.com/owner', '--output-dir', str(output), '--format', 'text']
            listed = [{'name': name} for name in ('app', 'summary', 'gone')]
            with patch.object(sources, 'repositories', return_value=(listed, skipped)), \
                 patch.object(sources, 'checkout', side_effect=checkout), \
                 patch.object(scanning, 'scan_repo', return_value=report([secret()])), \
                 contextlib.redirect_stdout(io.StringIO()) as printed:
                self.assertEqual(dso.main(argv), 2)
            summary = json.loads((output / 'summary.json').read_text())
            self.assertEqual([e['report'] for e in summary['repositories']], ['repos/app.json', 'repos/summary.json', None])
            self.assertEqual(summary['repositories'][2]['error_code'], 'not_found')
            self.assertEqual(summary['repositories'][0]['gate'], 'blocked')
            self.assertEqual((output / 'repos/app.json').stat().st_mode & 0o777, 0o600)
            for text in ('ORGANIZATION SCAN', '1 fork', 'MOST EXPOSED', 'FAILED  not_found'):
                self.assertIn(text, printed.getvalue())

    def test_organization_with_no_selected_repositories_is_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            argv = ['scan', 'org', 'https://github.com/owner', '--output-dir', folder]
            with patch.object(sources, 'repositories', return_value=([], {'fork': 1, 'archived': 0,
                                                                          'empty': 0, 'over_limit': 0})), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(dso.main(argv), 2)
            summary = json.loads((Path(folder) / 'summary.json').read_text())
            self.assertEqual(summary['repositories'], [])

    def test_menu_detects_github_targets_without_network(self):
        answers = ['', 'https://gitlab.com/a/b', 'github.com/owner/repo']
        style = console.Style(io.StringIO())
        self.assertEqual(console.menu(style, lambda prompt: answers.pop(0)), ['scan', 'https://github.com/owner/repo'])
        self.assertIn('only public GitHub repositories are supported', style.stream.getvalue())
        answers = ['1', 'https://github.com/owner/']
        self.assertEqual(console.menu(console.Style(io.StringIO()), lambda prompt: answers.pop(0)),
                         ['scan', 'https://github.com/owner'])


class ClassifierTests(unittest.TestCase):
    def test_paths_urls_and_images(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'app.py'
            file.write_text('x = 1\n')
            self.assertEqual(sources.classify(folder), ('directory', str(Path(folder).resolve())))
            self.assertEqual(sources.classify(str(file)), ('file', str(file.resolve())))
        self.assertEqual(sources.classify(' https://github.com/we45/Vulnerable-Flask-App '),
                         ('repository', 'https://github.com/we45/Vulnerable-Flask-App'))
        self.assertEqual(sources.classify('github.com/octocat'), ('account', 'https://github.com/octocat'))
        digest = 'sha256:' + 'a' * 64
        self.assertEqual(sources.classify(f'alpine@{digest}'), ('image', f'docker.io/library/alpine@{digest}'))
        self.assertEqual(sources.classify(f'ghcr.io/org/tool:1.0@{digest}'), ('image', f'ghcr.io/org/tool:1.0@{digest}'))
        for value in ('alpine', 'no/such/folder', '', 'https://gitlab.com/a/b'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                sources.classify(value)

    def test_tags_resolve_to_a_digest_anonymously(self):
        digest = 'sha256:' + 'b' * 64
        challenge = 'Bearer realm="https://auth.example/token",service="registry.example",scope="repository:library/alpine:pull"'
        calls = []

        class Response(io.BytesIO):
            def __init__(self, body=b'', headers=None):
                super().__init__(body)
                self.headers = headers or {}

        def urlopen(request, timeout=None):
            url = request if isinstance(request, str) else request.full_url
            calls.append((url, None if isinstance(request, str) else request.get_header('Authorization')))
            if url.startswith('https://auth.example/token?'):
                return Response(b'{"token": "anonymous"}')
            if request.get_header('Authorization') != 'Bearer anonymous':
                raise sources.urllib.error.HTTPError(url, 401, 'Unauthorized', {'WWW-Authenticate': challenge}, None)
            return Response(headers={'Docker-Content-Digest': digest})
        with patch.object(sources.urllib.request, 'urlopen', side_effect=urlopen):
            self.assertEqual(sources.classify('alpine:3.18'), ('image', f'docker.io/library/alpine:3.18@{digest}'))
        self.assertTrue(calls[0][0].startswith('https://registry-1.docker.io/v2/library/alpine/manifests/3.18'))
        self.assertIn('service=registry.example', calls[1][0])

    def test_scan_target_expands_with_defaults(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'DSO_REPORTS_DIR': folder}), \
             patch.object(scanning, 'preferred_profile', side_effect=lambda target: 'image' if target == 'image' else 'audit'):
            argv, detected = dso.expand_scan(['scan', folder, '--engine', 'docker'])
            self.assertEqual(argv[:3] + argv[3:5], ['scan', 'repo', str(Path(folder).resolve()), '--engine', 'docker'])
            self.assertEqual(argv[5:9], ['--project', Path(folder).name, '--profile', 'audit'])
            self.assertTrue(argv[-1].startswith(folder) and argv[-1].endswith('.json'))
            self.assertEqual(detected[0], 'directory')
            argv, _ = dso.expand_scan(['scan', 'https://github.com/owner/repo', '--output', 'r.json'])
            self.assertEqual(argv, ['scan', 'repo', 'https://github.com/owner/repo', '--output', 'r.json',
                                    '--project', 'github.com/owner/repo', '--profile', 'audit'])
            argv, _ = dso.expand_scan(['scan', 'https://github.com/owner'])
            self.assertEqual(argv[:3] + [argv[3]], ['scan', 'org', 'https://github.com/owner', '--profile'])
            self.assertIn('--output-dir', argv)
            image = 'ghcr.io/org/tool:1.0@sha256:' + 'c' * 64
            argv, _ = dso.expand_scan(['scan', image])
            self.assertEqual(argv[:7], ['scan', 'image', image, '--project', 'ghcr.io/org/tool', '--profile', 'image'])
            self.assertEqual(dso.expand_scan(['scan', 'repo', '.'])[0], ['scan', 'repo', '.'])
            argv, _ = dso.expand_scan(['scan', folder, '--project=team/app', '--output=r.json'])
            self.assertEqual(argv.count('--project'), 0)
            self.assertEqual([a for a in argv if a.startswith('--project')], ['--project=team/app'])
            self.assertNotIn('--output', argv)

    def test_preferred_profile_needs_every_scanner(self):
        with patch.object(scanning, 'executable_path', side_effect=lambda name: '/bin/' + name):
            self.assertEqual(scanning.preferred_profile('repo'), 'audit')
        with patch.object(scanning, 'executable_path', side_effect=lambda name: None if name == 'yr' else '/bin/' + name):
            self.assertEqual(scanning.preferred_profile('repo'), 'ci-blocking')
        self.assertEqual(scanning.preferred_profile('image'), 'image')

    def test_a_single_file_is_scanned_alone(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as work:
            (Path(folder) / 'secret.env').write_text('token')
            (Path(folder) / 'other.txt').write_text('x')
            destination = Path(work) / 'snapshot'
            evidence = runtime.snapshot(Path(folder) / 'secret.env', destination)
            self.assertEqual((evidence['files'], sorted(p.name for p in destination.iterdir())), (1, ['.semgrepignore', 'secret.env']))
            # Names that are skipped inside a tree are still scanned when asked for directly.
            for name in ('venv', '.gitignore', 'node_modules'):
                (Path(folder) / name).write_text('token')
                target = Path(work) / name
                self.assertEqual(runtime.snapshot(Path(folder) / name, target)['files'], 1, name)
                self.assertTrue((target / name).is_file())

if __name__ == '__main__':
    unittest.main()
