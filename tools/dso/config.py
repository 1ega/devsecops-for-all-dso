"""User settings: ~/.dso/config.json, environment variables and command-line options.

Precedence is option > environment > file > default. The file is read only from
the home directory (or DSO_CONFIG), never from a scanned target, and it must be
a regular file owned by the current user that nobody else can write.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile

import manifest
import runtime

ENGINES = ('native', 'docker')
DEFAULTS = {'reports_dir': '~/.dso/reports', 'cache_dir': None, 'engine': 'native', 'profile': None,
            'timeout': 300, 'max_report_mb': 20, 'max_findings': 50000}
RANGES = {'timeout': (1, 1800), 'max_report_mb': (20, 1024), 'max_findings': (1000, 1000000)}
ENVIRONMENT = {'reports_dir': 'DSO_REPORTS_DIR', 'cache_dir': 'DSO_CACHE_DIR',
               'max_report_mb': 'DSO_MAX_REPORT_MB', 'max_findings': 'DSO_MAX_FINDINGS'}
HELP = {'reports_dir': 'where the menu and dso scan TARGET save reports',
        'cache_dir': 'vulnerability database cache; null picks ~/.cache/dso',
        'engine': 'native or docker',
        'profile': 'default repository profile; null picks the most complete one that is installed',
        'timeout': 'seconds per plugin, 1-1800',
        'max_report_mb': 'largest report DSO writes or reads, 20-1024 MiB',
        'max_findings': 'most findings in one report, 1000-1000000'}


def path():
    return Path(os.environ.get('DSO_CONFIG') or Path.home() / '.dso' / 'config.json')


def check(key, value):
    """One validated setting; raises ValueError with the key named."""
    if key in RANGES:
        low, high = RANGES[key]
        if isinstance(value, bool) or type(value) is not int or not low <= value <= high:
            raise ValueError(f'{key} must be a whole number from {low} to {high}')
        return value
    if key == 'engine':
        if value not in ENGINES:
            raise ValueError('engine must be native or docker')
        return value
    if key == 'profile':
        if value is None:
            return None
        if not isinstance(value, str) or value not in manifest.profiles() or manifest.profile(value)['target'] != 'repo':
            repo = ', '.join(sorted(n for n, s in manifest.profiles().items() if s['target'] == 'repo'))
            raise ValueError('profile must be null or one of: ' + repo)
        return value
    if key in ('reports_dir', 'cache_dir'):
        if value is None and key == 'cache_dir':
            return None
        runtime.text(value, key, 4096)
        return str(Path(value).expanduser())
    raise ValueError(f'Unknown setting {key}')


def read_file(location):
    """The settings file, or {} when there is none."""
    try:
        info = location.lstat()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise ValueError(f'{location}: cannot read the settings file') from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ValueError(f'{location}: the settings file must be a regular file, not a symlink')
    if info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise ValueError(f'{location}: the settings file must be owned by you and not writable by others')
    # Keys starting with an underscore are comments, such as the _help block dso config init writes.
    data = {key: value for key, value in runtime.read_json(location).items() if not key.startswith('_')}
    unknown = sorted(set(data) - set(DEFAULTS))
    if unknown:
        raise ValueError(f'{location}: unknown settings {", ".join(unknown)}; known: {", ".join(DEFAULTS)}')
    return data


def load(overrides=None):
    """Effective settings and where each came from: 'default', 'file', 'environment' or 'option'."""
    values, sources = dict(DEFAULTS), {key: 'default' for key in DEFAULTS}
    location = path()
    for key, value in read_file(location).items():
        try:
            values[key] = check(key, value)
        except ValueError as exc:
            raise ValueError(f'{location}: {exc}') from None
        sources[key] = 'file'
    for key, variable in ENVIRONMENT.items():
        raw = os.environ.get(variable)
        if raw is None:
            continue
        if key in RANGES:
            if not raw.strip().isdigit():
                raise ValueError(f'{variable} must be a whole number')
            raw = int(raw)
        try:
            values[key] = check(key, raw)
        except ValueError as exc:
            raise ValueError(f'{variable}: {exc}') from None
        sources[key] = 'environment'
    for key, value in (overrides or {}).items():
        if value is not None:
            values[key] = check(key, value)
            sources[key] = 'option'
    values['reports_dir'] = str(Path(values['reports_dir']).expanduser())
    return values, sources


def apply(values):
    """Hand the limits to the modules that enforce them."""
    runtime.set_limits(values['max_report_mb'] * 1024 * 1024, values['max_findings'])
    return values


def write_defaults(location, force=False):
    """A settings file with every default spelled out, private to the user."""
    if location.exists() and not force:
        raise ValueError(f'{location} exists; pass --force to replace it')
    location.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    body = {'_help': HELP, **DEFAULTS}
    descriptor, temporary = tempfile.mkstemp(prefix='.dso-config-', dir=location.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(body, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, location)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return location
