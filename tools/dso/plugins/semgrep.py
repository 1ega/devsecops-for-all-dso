"""Semgrep: trusted kit rules with strict analysis and no target ignores or size limit."""
from __future__ import annotations

import os
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
    skipped = check_python(ctx.source_host)
    if not skipped:
        return
    # Preserve the original snapshot for every other scanner and for its input digest.
    # An exact filtered tree avoids glob patterns that could exclude more than these files.
    filtered = ctx.config_host.parent.parent / 'semgrep-source'
    shutil.copytree(ctx.source_host, filtered, copy_function=os.link)
    for path in skipped:
        (filtered / path).unlink()
    ctx.incomplete_files = skipped
    ctx.source_host = filtered
    if not ctx.inside:
        ctx.source = str(filtered)


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
    return [finding(plugin, item['check_id'], relative_path(item['path'], source),
                    severity(plugin, item['extra']['severity']), item['start']['line'],
                    cwe=cwe(item['extra'].get('metadata')))
            for item in data['results']]


def partial_paths(data, source):
    """Only file-local analysis errors can coexist with trusted findings."""
    if not isinstance(data, dict) or not isinstance(data.get('errors'), list):
        raise ValueError('Invalid Semgrep errors')
    paths = []
    for error in data['errors']:
        if not isinstance(error, dict):
            raise ValueError('Invalid Semgrep error')
        # Config, engine or other unlocalized errors must still fail the plugin.
        paths.append(relative_path(error['path'], source))
    return sorted(set(paths))
