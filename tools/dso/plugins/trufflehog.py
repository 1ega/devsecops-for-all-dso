"""TruffleHog: secrets in the snapshot with every detector, no verification and no inline ignores."""
from __future__ import annotations

import hashlib

from reports import finding, relative_path, severity

OPTIONS = {}
OUTPUT = 'stdout'
FORMAT = 'jsonl'


def policy_files(options, root):
    return []


def prepare(ctx):
    pass


def command(ctx):
    # Verification would send each secret to its provider; --no-ignore-tag stops trufflehog:ignore comments.
    return ['filesystem', ctx.source, '--json', '--no-update', '--no-verification', '--no-ignore-tag',
            '--no-color', '--fail', '--fail-on-scan-errors']


def parse(data, plugin, source):
    records = []
    for item in data:
        location = item['SourceMetadata']['Data']['Filesystem']
        # RawV2 holds the full credential when a detector needs two parts (key ID and secret).
        secret = item.get('RawV2') or item['Raw']
        if not isinstance(secret, str) or not secret or len(secret) > 1024 * 1024:
            raise ValueError('Invalid secret match')
        line = location.get('line', 0)
        fingerprint = hashlib.sha256(b'dso-secret-v2\0' + item['DetectorName'].encode() + b'\0' + secret.encode()).hexdigest()
        records.append(finding(plugin, item['DetectorName'], relative_path(location['file'], source), severity(plugin),
                               line if type(line) is int and line > 0 else 0, fingerprint=fingerprint))
    return records
