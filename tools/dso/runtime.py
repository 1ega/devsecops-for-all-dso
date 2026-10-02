"""Bounded input, private snapshots and cancellable scanner processes."""
from __future__ import annotations
import ast
import contextlib
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time

MAX_JSON = 20 * 1024 * 1024
MAX_FILE = 64 * 1024 * 1024
MAX_TREE = 2 * 1024 * 1024 * 1024
EXCLUDED = {'.git', '.venv', 'venv', '__pycache__', 'node_modules'}
IGNORE_FILES = {'.gitleaksignore', '.semgrepignore', '.gitignore'}


class ScanError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Cancelled(ScanError):
    def __init__(self):
        super().__init__('cancelled', 'Operation cancelled')


def check_cancel(event):
    if event is not None and event.is_set():
        raise Cancelled()


@contextlib.contextmanager
def signals():
    """Turn ordinary termination into stack unwinding; SIGKILL cannot be handled."""
    if threading.current_thread() is not threading.main_thread():
        yield
        return
    def stop(signum, frame):
        raise Cancelled()
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)}
    try:
        yield
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def loads(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('Duplicate JSON key')
            result[key] = value
        return result
    def bad_constant(value):
        raise ValueError('Non-finite JSON number')
    try:
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8-sig')
        if len(raw.encode('utf-8')) > MAX_JSON:
            raise ValueError('JSON input exceeds 20 MiB')
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)
    except (UnicodeError, RecursionError, json.JSONDecodeError) as exc:
        raise ValueError('Invalid or excessively nested JSON') from exc


def read_json(path):
    with Path(path).open('rb') as stream:
        data = loads(stream.read(MAX_JSON + 1))
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object')
    return data


def text(value, label, maximum=1024, empty=False):
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        raise ValueError(f'Invalid {label}')
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError(f'Control character in {label}')
    return value


def snapshot(target, destination, cancel=None, exclusions=()):
    """Never ask scanners to decide what unreadable files or target ignores mean."""
    target = target.resolve(strict=True)
    if not target.is_dir() or target == Path(target.anchor):
        raise ScanError('target', 'Target must be a non-root directory')
    if destination.resolve().is_relative_to(target):
        raise ScanError('target', 'Temporary workspace must be outside the scan target')
    excluded = set(exclusions)
    for value in excluded:
        text(value, 'exclusion')
        if Path(value).is_absolute() or '..' in Path(value).parts or value in ('.', ''):
            raise ValueError('Exclusions must be explicit target-relative paths')
    destination.mkdir(mode=0o700)
    count = size = 0
    manifest = hashlib.sha256()
    def walk(directory, relative):
        nonlocal count, size
        check_cancel(cancel)
        try:
            with os.scandir(directory) as entries:
                entries = sorted(entries, key=lambda e: e.name)
            for entry in entries:
                check_cancel(cancel)
                rel = (relative / entry.name).as_posix()
                try:
                    text(rel, 'source path', 4096)
                except ValueError:
                    raise ScanError('unsupported_path', 'A source path is too long or contains control characters; rename it or exclude a parent directory') from None
                if entry.name in EXCLUDED or rel in excluded:
                    continue
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    raise ScanError('symlink', f'Symlink is not scanned: {rel}; exclude it explicitly')
                if entry.name in IGNORE_FILES:
                    # Ignore content is not used, but unreadable inputs still fail.
                    with open(entry.path, 'rb') as stream:
                        stream.read(1)
                    continue
                info = entry.stat(follow_symlinks=False)
                output = destination / rel
                if stat.S_ISLNK(info.st_mode):
                    raise ScanError('symlink', f'Symlink is not scanned: {rel}; exclude it explicitly')
                if stat.S_ISDIR(info.st_mode):
                    if info.st_mode & 0o555 == 0:
                        raise PermissionError()
                    output.mkdir(mode=0o700)
                    walk(Path(entry.path), relative / entry.name)
                elif stat.S_ISREG(info.st_mode):
                    if info.st_mode & 0o444 == 0:
                        raise PermissionError()
                    fd = os.open(entry.path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                    with os.fdopen(fd, 'rb') as stream:
                        opened = os.fstat(stream.fileno())
                        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                            raise ScanError('changed_input', 'Source changed during snapshot')
                        data = stream.read(MAX_FILE + 1)
                        after = os.fstat(stream.fileno())
                    if len(data) > MAX_FILE or size + len(data) > MAX_TREE:
                        raise ScanError('input_limit', 'Snapshot exceeds the 64 MiB file or 2 GiB tree limit')
                    if (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                        raise ScanError('changed_input', 'Source changed during snapshot')
                    output.write_bytes(data)
                    output.chmod(0o600)
                    manifest.update(rel.encode() + b'\0' + hashlib.sha256(data).digest())
                    size += len(data)
                    count += 1
                    if count > 100000:
                        raise ScanError('input_limit', 'Snapshot exceeds 100000 files')
                else:
                    raise ScanError('special_file', f'Non-regular input is not scanned: {rel}')
        except (PermissionError, OSError) as exc:
            raise ScanError('unreadable_input', 'Source cannot be fully read; check file and directory permissions') from exc
    walk(target, Path())
    # An empty project-level file suppresses Semgrep's built-in ignores.
    (destination / '.semgrepignore').write_text('')
    return {'files': count, 'bytes': size, 'sha256': manifest.hexdigest()}


def check_python(source):
    """Make unsupported Python syntax visible rather than a zero-result pass."""
    for path in source.rglob('*.py'):
        try:
            ast.parse(path.read_bytes())
        except (SyntaxError, ValueError, RecursionError):
            raise ScanError('unsupported_python', 'Python syntax is unsupported; review and explicitly exclude templates/legacy Python') from None


def run_process(args, cwd, timeout, cancel=None, network_env=True):
    environment = {k: v for k, v in os.environ.items()
                   if not k.startswith(('SEMGREP_', 'TRIVY_', 'GITLEAKS_', 'GIT_'))}
    environment['PATH'] = os.pathsep.join([str(Path(sys.executable).parent), environment.get('PATH', '')])
    if sys.platform == 'darwin' and 'SSL_CERT_FILE' not in environment and Path('/etc/ssl/cert.pem').is_file():
        environment['SSL_CERT_FILE'] = '/etc/ssl/cert.pem'
    with tempfile.TemporaryDirectory(prefix='dso-state-') as state, tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
        # Scanner-owned temporary files must not outlive an interrupted run.
        environment.update(TMPDIR=state, SEMGREP_SETTINGS_FILE=str(Path(state) / 'settings.yml'),
                           SEMGREP_LOG_FILE=str(Path(state) / 'semgrep.log'),
                           SEMGREP_ENABLE_VERSION_CHECK='0', SEMGREP_SEND_METRICS='off')
        process = subprocess.Popen(args, cwd=cwd, env=environment, stdout=output, stderr=errors, start_new_session=True)
        try:
            deadline = time.monotonic() + timeout
            while process.poll() is None:
                check_cancel(cancel)
                if time.monotonic() >= deadline:
                    raise ScanError('timeout', 'Scanner exceeded its timeout')
                time.sleep(0.05)
            output.seek(0)
            errors.seek(0)
            diagnostic = errors.read(256 * 1024).lower()
            if b'permission denied' in diagnostic or b'operation not permitted' in diagnostic:
                raise ScanError('permissions', 'Scanner could not access required data')
            # A bare "429" also appears in ordinary counts such as "429 files".
            if b'too many requests' in diagnostic or b'toomanyrequests' in diagnostic:
                raise ScanError('rate_limit', 'Upstream service rate-limited the scanner')
            if b'no space left' in diagnostic:
                raise ScanError('disk_full', 'Scanner cache/output has insufficient space')
            return process.returncode, output.read(65536).decode('utf-8', errors='replace')
        finally:
            # Also kill grandchildren that outlived their immediate parent.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()
