"""Trivy image: OS and language package vulnerabilities of an image pulled by digest without credentials."""
from __future__ import annotations

import re

from reports import finding, relative_path, severity
from plugins.trivy import environment, prepare  # noqa: F401 (same empty configs and Docker isolation)

OPTIONS = {}


def policy_files(options, root):
    return []


def command(ctx):
    return ['image', '--image-src', 'remote', '--config', ctx.config + '/empty.yaml', '--scanners', 'vuln',
            '--cache-dir', ctx.cache, '--ignorefile', ctx.config + '/empty.ignore', '--format', 'json',
            '--exit-code', '0', '--output', ctx.output, ctx.source]


def parse(data, plugin, source):
    if not isinstance(data, dict) or data.get('SchemaVersion') != 2 or not isinstance((data.get('Results') or []), list):
        raise ValueError('Invalid Trivy report')
    records = []
    for result in (data.get('Results') or []):
        for item in result.get('Vulnerabilities') or []:
            # OS package targets name the image and its digest; os/<distribution> keeps IDs stable across rebuilds.
            if result.get('Class') == 'os-pkgs':
                if not re.fullmatch(r'[a-z0-9._-]{1,40}', str(result.get('Type'))):
                    raise ValueError('Unexpected OS type')
                path = f'os/{result["Type"]}'
            else:
                path = relative_path((item.get('PkgPath') or result['Target']).lstrip('/'), source)
            ids = item.get('CweIDs')
            cwe = [v for v in ids[:10] if isinstance(v, str) and re.fullmatch(r'CWE-[1-9][0-9]{0,4}', v)] \
                if isinstance(ids, list) else []
            records.append(finding(plugin, item['VulnerabilityID'], path, severity(plugin, item.get('Severity')),
                                   package=item['PkgName'], version=item.get('InstalledVersion') or '',
                                   fixed=item.get('FixedVersion') or '', cwe=cwe))
    return records
