"""Remote sources: public GitHub repositories fetched into a private directory for scanning.

Fetching is anonymous over HTTPS: system and user git configuration, credential
helpers and prompts are disabled, so no credential is ever sent. The tree is
written from git objects without a checkout, so no hook, filter, LFS, attribute
or submodule runs and nothing from the target executes. Paths that would
collide on this filesystem make the fetch fail instead of silently losing a file.
"""
from __future__ import annotations

import contextlib
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from runtime import (EXCLUDED, MAX_FILE, MAX_JSON, MAX_TREE, ScanError, check_cancel, environment, loads,
                     run_process, text)

API = 'https://api.github.com'
OWNER = r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})'
NAME = r'[A-Za-z0-9._-]{1,100}'
URL = re.compile(rf'(?:https://)?(?:www\.)?github\.com/(?P<owner>{OWNER})(?:/(?P<repo>{NAME}))?')
COMMIT = re.compile('[a-f0-9]{40}|[a-f0-9]{64}')
FETCH_TIMEOUT = 900
MAX_FILES = 100000
MAX_REPOSITORIES = 1000
# Anonymous HTTPS only, whatever the caller's git configuration says.
GIT_ENV = {'GIT_TERMINAL_PROMPT': '0', 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
           'GIT_ASKPASS': '', 'SSH_ASKPASS': '', 'GIT_LFS_SKIP_SMUDGE': '1', 'GIT_NO_REPLACE_OBJECTS': '1'}
GIT_CONFIG = ['-c', 'credential.helper=', '-c', 'protocol.allow=never', '-c', 'protocol.https.allow=always',
              '-c', 'transfer.fsckObjects=true', '-c', 'core.hooksPath=' + os.devnull, '-c', 'advice.detachedHead=false']


def is_remote(value):
    return isinstance(value, str) and value.strip().lower().startswith(('https://', 'http://', 'git@', 'github.com/', 'www.github.com/'))


def parse(value):
    """(owner, repository or None) from a github.com URL; ValueError for anything else."""
    if not isinstance(value, str):
        raise ValueError('Expected a GitHub URL')
    value = value.strip()
    value = value[:-1] if value.endswith('/') else value
    value = value[:-4] if value.endswith('.git') else value
    match = URL.fullmatch(value)
    if not match or match['repo'] in ('.', '..'):
        raise ValueError('Use https://github.com/OWNER/REPOSITORY or https://github.com/OWNER; '
                         'only public GitHub repositories are supported')
    return match['owner'], match['repo']


TAGGED = re.compile(r'[a-z0-9]+(?:[._/-][a-z0-9]+)*(?::[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})?(?:@sha256:[a-f0-9]{64})?')
DIGEST = re.compile(r'sha256:[a-f0-9]{64}')


def classify(value):
    """What a person typed: ('directory'|'file'|'repository'|'account'|'image', normalized value)."""
    value = value.strip() if isinstance(value, str) else ''
    if not value:
        raise ValueError('Give a folder, a file, a GitHub URL or an image')
    path = Path(value).expanduser()
    if path.is_dir():
        return 'directory', str(path.resolve())
    if path.is_file():
        return 'file', str(path.resolve())
    if is_remote(value):
        owner, name = parse(value)
        return ('repository', f'https://github.com/{owner}/{name}') if name else ('account', f'https://github.com/{owner}')
    if looks_like_image(value):
        return 'image', resolve_image(value)
    raise ValueError(f'No such folder or file. For an image add a tag, for example {value}:latest; '
                     'for GitHub paste https://github.com/OWNER/REPO')


def split_image(value):
    """(registry, repository, tag, digest); Docker Hub names get docker.io and library/."""
    name, _, digest = value.partition('@')
    first, _, rest = name.partition('/')
    registry = first if rest and ('.' in first or ':' in first or first == 'localhost') else 'docker.io'
    path = rest if registry == first else name
    tag = ''
    if ':' in path.rsplit('/', 1)[-1]:
        path, tag = path.rsplit(':', 1)
    if registry == 'docker.io' and '/' not in path:
        path = 'library/' + path
    return registry, path, tag, digest


def looks_like_image(value):
    """A tag, a digest or a registry host; a bare word is more likely a mistyped folder."""
    registry, _, tag, digest = split_image(value)
    explicit = '/' in value and value.split('/', 1)[0] == registry
    name = value.split('/', 1)[1] if explicit else value
    return bool(TAGGED.fullmatch(name)) and bool(tag or digest or explicit)


def resolve_image(value):
    """Pin an image by digest with an anonymous registry request; a given digest is kept as is."""
    registry, repository, tag, digest = split_image(value)
    if digest:
        if not DIGEST.fullmatch(digest):
            raise ValueError('Invalid image digest')
        return f'{registry}/{repository}' + (f':{tag}' if tag else '') + f'@{digest}'
    tag = tag or 'latest'
    host = 'registry-1.docker.io' if registry == 'docker.io' else registry
    url = f'https://{host}/v2/{repository}/manifests/{tag}'
    accept = ', '.join(('application/vnd.oci.image.index.v1+json', 'application/vnd.docker.distribution.manifest.list.v2+json',
                        'application/vnd.oci.image.manifest.v1+json', 'application/vnd.docker.distribution.manifest.v2+json'))
    headers = {'Accept': accept, 'User-Agent': 'dso'}
    try:
        try:
            response = urllib.request.urlopen(urllib.request.Request(url, headers=headers, method='HEAD'), timeout=30)
        except urllib.error.HTTPError as exc:
            exc.close()
            challenge = exc.headers.get('WWW-Authenticate', '') if exc.code == 401 else ''
            fields = dict(re.findall(r'(\w+)="([^"]*)"', challenge))
            if not challenge.lower().startswith('bearer') or not fields.get('realm', '').startswith('https://'):
                raise
            query = urllib.parse.urlencode({k: v for k, v in fields.items() if k in ('service', 'scope')})
            with urllib.request.urlopen(f'{fields["realm"]}?{query}', timeout=30) as answer:
                token = loads(answer.read(MAX_JSON + 1))
            token = token.get('token') or token.get('access_token') if isinstance(token, dict) else None
            if not isinstance(token, str):
                raise ScanError('registry', 'The registry did not grant anonymous access') from None
            response = urllib.request.urlopen(urllib.request.Request(url, headers=dict(headers, Authorization='Bearer ' + token),
                                                                     method='HEAD'), timeout=30)
        with response:
            digest = response.headers.get('Docker-Content-Digest', '')
    except urllib.error.HTTPError as exc:
        exc.close()
        if exc.code in (401, 403, 404):
            raise ScanError('not_found', f'Image {value} was not found or is not public') from None
        raise ScanError('registry', f'The registry answered HTTP {exc.code}') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ScanError('network', f'{registry} is unreachable; check the network or proxy settings') from None
    if not DIGEST.fullmatch(digest):
        raise ScanError('registry', 'The registry did not return a digest')
    return f'{registry}/{repository}:{tag}@{digest}'


def project_id(owner, name):
    return f'github.com/{owner}/{name}'


def api(path):
    request = urllib.request.Request(API + path, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'dso',
                                                          'X-GitHub-Api-Version': '2022-11-28'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read(MAX_JSON + 1)
    except urllib.error.HTTPError as exc:
        exc.close()
        if exc.code == 404:
            raise ScanError('not_found', 'Not found on GitHub, or private; DSO fetches public repositories only') from None
        if exc.code in (403, 429) and exc.headers.get('X-RateLimit-Remaining') == '0':
            raise ScanError('rate_limit', 'GitHub allows 60 anonymous API requests per hour; try again later') from None
        raise ScanError('github', f'GitHub API answered HTTP {exc.code}') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ScanError('network', 'GitHub is unreachable; check the network or proxy settings') from None
    return loads(raw)


def check_repository(data, owner):
    if not isinstance(data, dict):
        raise ScanError('github', 'Unexpected GitHub API response')
    fields = {'name': str, 'private': bool, 'archived': bool, 'fork': bool, 'size': int}
    if (any(type(data.get(k)) is not t for k, t in fields.items()) or not re.fullmatch(NAME, data['name'])
            or data['size'] < 0
            or data['name'] in ('.', '..')):
        raise ScanError('github', 'Unexpected GitHub API response')
    login = data.get('owner', {}).get('login') if isinstance(data.get('owner'), dict) else None
    if not isinstance(login, str) or login.lower() != owner.lower():
        raise ScanError('github', 'GitHub returned a repository of another owner')
    return data


def repository(owner, name):
    data = check_repository(api(f'/repos/{owner}/{name}'), owner)
    if data['private']:
        raise ScanError('private', 'Private repositories are not supported yet')
    return data


def repositories(owner, include_forks=False, include_archived=False, limit=50):
    """Validated public repository metadata from the paginated account listing."""
    if type(limit) is not int or not 1 <= limit <= MAX_REPOSITORIES:
        raise ValueError(f'Limit must be 1-{MAX_REPOSITORIES}')
    account = api(f'/users/{owner}')
    if not isinstance(account, dict) or account.get('type') not in ('User', 'Organization'):
        raise ScanError('github', 'Unexpected GitHub API response')
    base = f'/orgs/{owner}/repos?type=public' if account['type'] == 'Organization' else f'/users/{owner}/repos?type=owner'
    selected, skipped = [], {'fork': 0, 'archived': 0, 'empty': 0, 'over_limit': 0}
    for page in range(1, MAX_REPOSITORIES // 100 + 2):
        batch = api(f'{base}&sort=full_name&per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ScanError('github', 'Unexpected GitHub API response')
        for item in batch:
            data = check_repository(item, owner)
            if data['private']:
                continue
            reason = ('fork' if data['fork'] and not include_forks else
                      'archived' if data['archived'] and not include_archived else
                      'empty' if data['size'] == 0 else
                      'over_limit' if len(selected) >= limit else None)
            if reason:
                skipped[reason] += 1
            else:
                selected.append(data)
        if len(batch) < 100:
            break
    return selected, skipped


def clone_url(owner, name):
    return f'https://github.com/{owner}/{name}.git'


def git_executable():
    git = shutil.which('git')
    if not git:
        raise ScanError('missing_executable', 'git is required to fetch remote repositories')
    return git


def tree_entries(listing, exclusions):
    """Regular files to write from `git ls-tree -r -z -l`; symlinks and submodules carry no content."""
    files, total = [], 0
    excluded = set(exclusions)
    for record in listing.split(b'\0'):
        if not record:
            continue
        meta, _, raw = record.partition(b'\t')
        try:
            mode, kind, oid, size = meta.decode('ascii').split()
            path = raw.decode('utf-8')
        except (UnicodeError, ValueError):
            raise ScanError('unsupported_path', 'A repository path is not valid UTF-8') from None
        try:
            text(path, 'source path', 4096)
        except ValueError:
            raise ScanError('unsupported_path', 'A repository path is too long or contains control characters') from None
        parts = path.split('/')
        if any(p in ('', '.', '..') or p.lower() == '.git' for p in parts):
            raise ScanError('unsupported_path', 'A repository path is not a plain relative path')
        if kind != 'blob' or mode == '120000':
            continue
        if any(p in EXCLUDED for p in parts[:-1]) or any('/'.join(parts[:i]) in excluded for i in range(1, len(parts) + 1)):
            continue
        if not COMMIT.fullmatch(oid) or not size.isdigit():
            raise ScanError('fetch', 'Unexpected git tree listing')
        size = int(size)
        total += size
        if size > MAX_FILE or total > MAX_TREE or len(files) >= MAX_FILES:
            raise ScanError('input_limit', 'Repository exceeds the 64 MiB file, 2 GiB tree or 100000 file limit')
        files.append((path, oid, size))
    return files


def write_blobs(git, bare, files, destination, deadline, cancel=None):
    """Stream blobs with one `git cat-file --batch`; O_EXCL turns path collisions into errors."""
    with tempfile.TemporaryDirectory(prefix='dso-state-') as state:
        process = subprocess.Popen([git, *GIT_CONFIG, '-C', str(bare), 'cat-file', '--batch'],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                   env=environment(state, GIT_ENV), start_new_session=True)

        def feed():
            try:
                for _, oid, _ in files:
                    process.stdin.write(oid.encode() + b'\n')
                process.stdin.close()
            except OSError:
                pass

        threading.Thread(target=feed, daemon=True).start()
        timer = threading.Timer(max(1.0, deadline - time.monotonic()), process.kill)
        timer.start()
        try:
            for path, oid, size in files:
                check_cancel(cancel)
                if time.monotonic() >= deadline:
                    raise ScanError('timeout', 'Fetching the repository exceeded its timeout')
                header = process.stdout.readline(256).split()
                if header != [oid.encode(), b'blob', str(size).encode()]:
                    raise ScanError('fetch', 'Repository objects are missing or inconsistent')
                target = destination / path
                try:
                    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
                    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
                except (FileExistsError, NotADirectoryError):
                    raise ScanError('path_collision', 'Two repository paths map to the same file on this filesystem '
                                    '(for example names differing only in case)') from None
                with os.fdopen(descriptor, 'wb') as output:
                    remaining = size
                    while remaining:
                        chunk = process.stdout.read(min(remaining, 1 << 20))
                        if not chunk:
                            raise ScanError('fetch', 'Repository objects ended early')
                        output.write(chunk)
                        remaining -= len(chunk)
                if process.stdout.read(1) != b'\n':
                    raise ScanError('fetch', 'Unexpected git object stream')
        except ScanError as exc:
            if exc.code == 'fetch' and time.monotonic() >= deadline:
                raise ScanError('timeout', 'Fetching the repository exceeded its timeout') from None
            raise
        finally:
            timer.cancel()
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass  # already exited; macOS reports an unreaped group as EPERM
            process.wait()
            process.stdout.close()


def fetch(owner, name, work, exclusions=(), cancel=None, metadata=None):
    """Write the default branch tree into work/tree; returns (tree, origin, files)."""
    data = check_repository(metadata, owner) if metadata is not None else repository(owner, name)
    if data['name'].lower() != name.lower() or data['private']:
        raise ScanError('github', 'Repository listing does not match the requested public repository')
    # The API size is the repository with history in KiB; a shallow fetch is smaller.
    if data['size'] * 1024 > 4 * MAX_TREE:
        raise ScanError('input_limit', 'Repository is too large to fetch')
    git = git_executable()
    bare, tree = work / 'repo.git', work / 'tree'
    deadline = time.monotonic() + FETCH_TIMEOUT
    code, _ = run_process([git, *GIT_CONFIG, 'clone', '--bare', '--depth', '1', '--single-branch', '--no-tags',
                           '--quiet', '--', clone_url(owner, data['name']), str(bare)], work, FETCH_TIMEOUT, cancel, GIT_ENV)
    if code:
        raise ScanError('fetch', 'git could not fetch the repository')
    code, commit = run_process([git, *GIT_CONFIG, '-C', str(bare), 'rev-parse', '--verify', 'HEAD^{commit}'],
                               work, 60, cancel, GIT_ENV)
    commit = commit.strip()
    if code or not COMMIT.fullmatch(commit):
        raise ScanError('fetch', 'Repository has no default branch commit')
    listing = work / 'tree.list'
    code, _ = run_process([git, *GIT_CONFIG, '-C', str(bare), 'ls-tree', '-r', '-z', '-l', '--full-tree', commit],
                          work, 300, cancel, GIT_ENV, output_path=listing)
    if code:
        raise ScanError('fetch', 'git could not list the repository tree')
    files = tree_entries(listing.read_bytes(), exclusions)
    tree.mkdir(mode=0o700)
    write_blobs(git, bare, files, tree, deadline, cancel)
    return tree, {'url': f'https://github.com/{owner}/{data["name"]}', 'commit': commit}, files


@contextlib.contextmanager
def checkout(owner, name, exclusions=(), cancel=None, progress=None, metadata=None):
    """Yield (directory, origin) for the default branch of a public repository; removed afterwards."""
    if progress is not None:
        progress('start', 'fetch', None)
    with tempfile.TemporaryDirectory(prefix='dso-fetch-') as folder:
        try:
            tree, origin, files = fetch(owner, name, Path(folder), exclusions, cancel, metadata)
        except ScanError as exc:
            if progress is not None:
                progress('done', 'fetch', {'status': 'error', 'error_code': exc.code, 'error': str(exc)})
            raise
        if progress is not None:
            progress('done', 'fetch', {'status': 'complete', 'commit': origin['commit'], 'files': len(files),
                                       'bytes': sum(size for _, _, size in files)})
        yield tree, origin
