"""Grype: dependency vulnerabilities in the snapshot with an explicit configuration and no registry credentials."""
from __future__ import annotations

import json
import re

from reports import canonical_advisory, finding, relative_path, severity

OPTIONS = {}


def policy_files(options, root):
    return []


def prepare(ctx):
    # An explicit file stops grype from reading .grype.yaml or user configuration.
    (ctx.config_host / 'grype.yaml').write_text(
        f'check-for-app-update: false\ndb:\n  cache-dir: {json.dumps(ctx.cache + "/grype")}\n  auto-update: true\n')
    (ctx.config_host / 'docker').mkdir(mode=0o700)


def environment(ctx):
    return {'DOCKER_CONFIG': ctx.config + '/docker'}


def command(ctx):
    return ['dir:' + ctx.source, '--config', ctx.config + '/grype.yaml', '--output', 'json', '--file', ctx.output, '--quiet']


def parse(data, plugin, source):
    if not isinstance(data, dict) or not isinstance(data.get('matches'), list):
        raise ValueError('Invalid Grype report')
    records = []
    for match in data['matches']:
        vulnerability, artifact = match['vulnerability'], match['artifact']
        if not isinstance(artifact.get('locations'), list) or not artifact['locations']:
            raise ValueError('Grype match has no package location')
        # Directory scans report locations from the scanned root, such as /package-lock.json.
        path = relative_path(artifact['locations'][0]['path'].lstrip('/'), source)
        fix = vulnerability.get('fix') or {}
        fixed = fix['versions'][0] if fix.get('state') == 'fixed' and fix.get('versions') else ''
        cwe = sorted({c['cwe'] for c in vulnerability.get('cwes') or []
                      if isinstance(c, dict) and isinstance(c.get('cwe'), str) and re.fullmatch(r'CWE-[1-9][0-9]{0,4}', c['cwe'])})
        # GitHub advisories come as GHSA IDs with the CVE among the match's related records; Trivy reports the CVE.
        related = [r.get('id') for r in match.get('relatedVulnerabilities') or [] if isinstance(r, dict)]
        records.append(finding(plugin, canonical_advisory(vulnerability['id'], related), path,
                               severity(plugin, vulnerability.get('severity')),
                               package=artifact['name'], version=artifact['version'], fixed=fixed, cwe=cwe[:10]))
    return records
