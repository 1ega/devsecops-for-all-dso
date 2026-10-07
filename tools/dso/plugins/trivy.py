"""Trivy: filesystem dependency vulnerabilities in offline mode with empty ignore and config files."""
from __future__ import annotations

import re

from reports import finding, relative_path, severity

OPTIONS = {}


def policy_files(options, root):
    return []


def prepare(ctx):
    (ctx.config_host / 'empty.yaml').write_text('{}\n')
    (ctx.config_host / 'empty.ignore').write_text('')


def command(ctx):
    return ['fs', '--config', ctx.config + '/empty.yaml', '--scanners', 'vuln',
            '--offline-scan', '--cache-dir', ctx.cache,
            '--ignorefile', ctx.config + '/empty.ignore', '--format', 'json',
            '--exit-code', '0', '--output', ctx.output, ctx.source]


def parse(data, plugin, source):
    if not isinstance(data, dict) or data.get('SchemaVersion') != 2 or not isinstance((data.get('Results') or []), list) or not data.get('ArtifactName'):
        raise ValueError('Invalid Trivy report')
    records = []
    for result in (data.get('Results') or []):
        path = relative_path(result['Target'], source)
        for item in result.get('Vulnerabilities') or []:
            ids = item.get('CweIDs')
            cwe = [v for v in ids[:10] if isinstance(v, str) and re.fullmatch(r'CWE-[1-9][0-9]{0,4}', v)] \
                if isinstance(ids, list) else []
            records.append(finding(plugin, item['VulnerabilityID'], path, severity(plugin, item.get('Severity')),
                                   package=item['PkgName'], version=item.get('InstalledVersion') or '',
                                   fixed=item.get('FixedVersion') or '', cwe=cwe))
    return records
