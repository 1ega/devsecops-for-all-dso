"""The exception register: time-boxed waivers with an owner and a different approver.

One entry waives one rule of one tool for one asset until it expires, at most 90 days after it
was created. Applied to a gate (see reports.waive), an active entry stops the findings it matches
from blocking whatever their severity, because a reviewed and approved decision outranks a
scanner's guess. A malformed register waives nothing and fails the gate; an expired entry waives
nothing and is listed, so the pressure to revisit a decision stays visible. The file is private,
like a baseline, and is never read from the scanned target.
"""
from __future__ import annotations

from datetime import date
import json
import os
from pathlib import Path
import re
import tempfile

import runtime

FIELDS = ('id', 'tool', 'rule_id', 'asset_id', 'owner', 'approver', 'reason', 'compensating_control', 'ticket',
          'created_on', 'expires_on')
TEXT = FIELDS[:9]
MAX_DAYS = 90
# An exception this close to its expiry is pointed out in the gate summary.
SOON = 14
ANY = '*'


def parse_date(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'{label}: expected YYYY-MM-DD')
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f'{label}: expected YYYY-MM-DD') from None


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def problems(register, today=None):
    """Every problem of a register as (kind, message): 'structure' for what makes an entry unusable,
    'expired' for entries whose date has passed. Malformed shapes raise instead."""
    today = today or date.today()
    entries = register.get('exceptions') if isinstance(register, dict) else None
    if not isinstance(entries, list):
        raise ValueError('exceptions must be a list')
    found, seen, scopes = [], set(), set()
    for number, entry in enumerate(entries, start=1):
        label = f'exception {number}'
        if not isinstance(entry, dict):
            raise ValueError(f'{label}: expected an object')
        for field in TEXT:
            if not nonempty(entry.get(field)):
                found.append(('structure', f'{label}: missing {field}'))
                continue
            try:
                runtime.text(entry[field], field, 512)
            except ValueError:
                found.append(('structure', f'{label}: {field} is too long or contains control characters'))
        if nonempty(entry.get('owner')) and nonempty(entry.get('approver')) and \
                entry['owner'].strip().casefold() == entry['approver'].strip().casefold():
            found.append(('structure', f'{label}: owner and approver must differ'))
        if nonempty(entry.get('id')):
            identifier = entry['id'].strip().casefold()
            if identifier in seen:
                found.append(('structure', f'{label}: duplicate id {identifier}'))
            seen.add(identifier)
        scope = tuple(str(entry.get(k, '')).strip().casefold() for k in ('tool', 'rule_id', 'asset_id'))
        if scope in scopes:
            found.append(('structure', f'{label}: duplicate exception scope'))
        scopes.add(scope)
        try:
            created = parse_date(entry.get('created_on'), f'{label}.created_on')
            expires = parse_date(entry.get('expires_on'), f'{label}.expires_on')
        except ValueError as exc:
            found.append(('structure', str(exc)))
            continue
        if created > today:
            found.append(('structure', f'{label}: creation date in future'))
        if expires <= today:
            found.append(('expired', f'{label}: expired'))
        if expires <= created or (expires - created).days > MAX_DAYS:
            found.append(('structure', f'{label}: expiry must be 1–90 days after creation'))
    return found


def load(path, today=None):
    """Entries a gate may apply. Any structural problem refuses the whole file: a register that
    cannot be trusted as a whole waives nothing."""
    register = runtime.read_json(Path(path))
    structural = [message for kind, message in problems(register, today) if kind == 'structure']
    if structural:
        raise ValueError(f'{path}: exception register rejected: ' + '; '.join(structural[:5])
                         + (f' and {len(structural) - 5} more' if len(structural) > 5 else ''))
    return register['exceptions']


def matches(entry, finding, project):
    """tool and asset_id accept * for any; rule_id must be exact."""
    return (entry['tool'] in (ANY, finding['plugin']) and entry['rule_id'] == finding['rule_id']
            and (entry['asset_id'] == ANY or entry['asset_id'].casefold() == project.casefold()))


def active(entry, today=None):
    return parse_date(entry['expires_on'], 'expires_on') > (today or date.today())


def read(path):
    """The entries of an existing register, or none for a file that does not exist yet."""
    path = Path(path)
    if not path.exists():
        return []
    register = runtime.read_json(path)
    structural = [message for kind, message in problems(register) if kind == 'structure']
    if structural:
        raise ValueError(f'{path}: fix the register before adding to it: ' + '; '.join(structural[:5]))
    return register['exceptions']


def write(path, entries):
    """Replace the register atomically; private to the user like a report."""
    path = Path(path)
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError('The register must be a regular file, not a symlink or device')
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix='.dso-register-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump({'exceptions': entries}, stream, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


def next_id(entries, today=None):
    today = today or date.today()
    taken = {str(e.get('id', '')).casefold() for e in entries}
    number = 1
    while f'exc-{today:%Y%m%d}-{number}' in taken:
        number += 1
    return f'EXC-{today:%Y%m%d}-{number}'
