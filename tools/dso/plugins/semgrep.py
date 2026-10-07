"""Semgrep: trusted kit rules with strict analysis and no target ignores or size limit."""
from __future__ import annotations

import re
import shutil

from reports import finding, relative_path, severity
from runtime import check_python

OPTIONS = {'rules': 'dirs'}


def policy_files(options, root):
    return sorted(p for directory in options['rules'] for p in (root / directory).rglob('*')
                  if p.suffix in ('.yaml', '.yml') and not p.name.endswith(('.test.yaml', '.test.yml')))


def prepare(ctx):
    # Only trusted rule files are exposed to the scanner, never the whole kit.
    rules = policy_files(ctx.options, ctx.root)
    if not rules:
        raise ValueError('No trusted Semgrep rules found')
    for i, rule in enumerate(rules):
        shutil.copyfile(rule, ctx.config_host / f'rule-{i}.yaml')


def preflight(ctx):
    check_python(ctx.source_host)


def command(ctx):
    rules = sorted(p.name for p in ctx.config_host.glob('rule-*.yaml'))
    return ['scan', '--metrics=off', '--disable-version-check', '--strict',
            '--disable-nosem', '--no-rewrite-rule-ids', '--no-git-ignore',
            '--max-target-bytes', '0', '--json', '--output', ctx.output,
            *[v for name in rules for v in ('--config', f'{ctx.config}/{name}')], ctx.source]


def cwe(metadata):
    """CWE IDs from trusted rule metadata such as 'CWE-295: Improper Certificate Validation'."""
    values = metadata.get('cwe', []) if isinstance(metadata, dict) else []
    values = [values] if isinstance(values, str) else values if isinstance(values, list) else []
    return sorted({m.group(1) for v in values[:10] if isinstance(v, str)
                   for m in [re.match(r'(CWE-[1-9][0-9]{0,4})(?![0-9])', v)] if m})


def parse(data, plugin, source):
    if not isinstance(data, dict) or not isinstance(data.get('results'), list) or not isinstance(data.get('errors'), list):
        raise ValueError('Invalid Semgrep report')
    if data['errors']:
        raise ValueError('Semgrep reported incomplete analysis')
    return [finding(plugin, item['check_id'], relative_path(item['path'], source),
                    severity(plugin, item['extra']['severity']), item['start']['line'],
                    cwe=cwe(item['extra'].get('metadata')))
            for item in data['results']]
