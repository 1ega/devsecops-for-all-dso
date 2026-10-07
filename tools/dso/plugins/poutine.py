"""poutine: CI/CD pipeline weaknesses in GitHub Actions, GitLab CI, Azure Pipelines and Tekton files."""
from __future__ import annotations

from reports import finding, relative_path, severity

OPTIONS = {}
OUTPUT = 'stdout'


def policy_files(options, root):
    return []


def prepare(ctx):
    # An explicit config stops poutine from reading .poutine.yml skip rules from the target or this directory.
    (ctx.config_host / 'poutine.yml').write_text('skip: []\n')


def command(ctx):
    return ['analyze_local', ctx.source, '--format', 'json', '--quiet', '--disable-version-check',
            '--fail-on-violation', '--config', ctx.config + '/poutine.yml']


def parse(data, plugin, source):
    if not isinstance(data, dict) or not isinstance(data.get('findings'), list) or not isinstance(data.get('rules'), dict):
        raise ValueError('Invalid poutine report')
    records = []
    for item in data['findings']:
        meta = item['meta']
        rule = data['rules'].get(item['rule_id'])
        line = meta.get('line', 0)
        records.append(finding(plugin, item['rule_id'], relative_path(meta['path'], source),
                               severity(plugin, rule.get('level') if isinstance(rule, dict) else None),
                               line if type(line) is int and line > 0 else 0))
    return records
