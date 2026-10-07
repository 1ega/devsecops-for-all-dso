"""Gitleaks: secrets in the snapshot with the reviewed config and no target allowlists."""
from __future__ import annotations

import hashlib

from reports import finding, relative_path, severity

OPTIONS = {'config': 'file'}
# The upstream config allowlists files named gitleaks.toml; remove that path without editing the import.
SELF_ALLOWLIST = "    '''gitleaks\\.toml''',\n"


def policy_files(options, root):
    return [root / options['config']]


def prepare(ctx):
    config = (ctx.root / ctx.options['config']).read_text()
    (ctx.config_host / 'gitleaks.toml').write_text(config.replace(SELF_ALLOWLIST, ''))
    (ctx.config_host / 'empty.ignore').write_text('')


def command(ctx):
    return ['dir', '--no-banner', '--redact=0', '--exit-code', str(ctx.spec['exit_codes']['findings']),
            '--config', ctx.config + '/gitleaks.toml',
            '--ignore-gitleaks-allow', '--gitleaks-ignore-path', ctx.config + '/empty.ignore',
            '--report-format', 'json', '--report-path', ctx.output, ctx.source]


def parse(data, plugin, source):
    if not isinstance(data, list):
        raise ValueError('Gitleaks report must be an array')
    records = []
    for item in data:
        # Multi-line secrets (PEM keys) are valid; only the domain-separated hash is kept.
        secret = item['Secret']
        if not isinstance(secret, str) or not secret or len(secret) > 1024 * 1024:
            raise ValueError('Invalid secret match')
        fingerprint = hashlib.sha256(b'dso-secret-v2\0' + item['RuleID'].encode() + b'\0' + secret.encode()).hexdigest()
        records.append(finding(plugin, item['RuleID'], relative_path(item['File'], source),
                               severity(plugin), item['StartLine'], fingerprint=fingerprint))
    return records
