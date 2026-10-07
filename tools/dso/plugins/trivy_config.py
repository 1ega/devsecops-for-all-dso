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
            '--ignorefile', ctx.config + '/empty.ignore', '--format', 'json', '--exit-code', '0',
            '--output', ctx.output, ctx.source]


def parse(data, plugin, source):
    if not isinstance(data, dict) or data.get('SchemaVersion') != 2 or not isinstance((data.get('Results') or []), list):
        raise ValueError('Invalid Trivy report')
    records = []
    for result in (data.get('Results') or []):
        path = relative_path(result['Target'], source)
        for item in result.get('Misconfigurations') or []:
            if item.get('Status') != 'FAIL':
                continue
            line = (item.get('CauseMetadata') or {}).get('StartLine', 0)
            records.append(finding(plugin, item['ID'], path, severity(plugin, item.get('Severity')),
                                   line if type(line) is int and line > 0 else 0))
    return records
