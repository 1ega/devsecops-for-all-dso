"""Trivy config: IaC misconfigurations with the checks embedded in the pinned binary."""
from __future__ import annotations

from reports import finding, relative_path, severity

OPTIONS = {}


def policy_files(options, root):
    return []


def prepare(ctx):
    (ctx.config_host / 'empty.yaml').write_text('{}\n')
    (ctx.config_host / 'empty.ignore').write_text('')


def command(ctx):
    # An empty private cache with --skip-check-update always uses the checks embedded in this version.
    return ['config', '--config', ctx.config + '/empty.yaml', '--skip-check-update', '--cache-dir', ctx.config + '/cache',
            # SARIF records failures without repeating Trivy's large cause/code blocks per finding.
            '--ignorefile', ctx.config + '/empty.ignore', '--format', 'sarif', '--exit-code', '0',
            '--output', ctx.output, ctx.source]


def parse(data, plugin, source):
    if not isinstance(data, dict) or data.get('version') != '2.1.0' or not isinstance(data.get('runs'), list) or len(data['runs']) != 1:
        raise ValueError('Invalid Trivy SARIF report')
    run = data['runs'][0]
    if not isinstance(run.get('results'), list) or not isinstance(run.get('tool', {}).get('driver', {}).get('rules'), list):
        raise ValueError('Invalid Trivy SARIF results')
    rules = {rule['id']: rule for rule in run['tool']['driver']['rules']}
    records = []
    for item in run['results']:
        rule_id = item['ruleId']
        tags = rules[rule_id].get('properties', {}).get('tags') or []
        native = next((tag for tag in tags if tag in ('UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')), None)
        location = item['locations'][0]['physicalLocation']
        artifact = location['artifactLocation']
        if artifact.get('uriBaseId') != 'ROOTPATH':
            raise ValueError('Trivy SARIF location is not under the scanned root')
        line = location.get('region', {}).get('startLine', 0)
        records.append(finding(plugin, rule_id, relative_path(artifact['uri'], source), severity(plugin, native),
                               line if type(line) is int and line > 0 else 0))
    return records
