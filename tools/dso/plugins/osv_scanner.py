"""OSV-Scanner: lockfile vulnerabilities checked against downloaded OSV databases; no package list is sent."""
from __future__ import annotations

import re

from reports import canonical_advisory, finding, relative_path, severity

OPTIONS = {}
RANK = ('LOW', 'MODERATE', 'MEDIUM', 'HIGH', 'CRITICAL')


def policy_files(options, root):
    return []


def prepare(ctx):
    # An explicit empty config overrides osv-scanner.toml ignore entries in the target.
    (ctx.config_host / 'osv-scanner.toml').write_text('')


def environment(ctx):
    return {'OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY': ctx.cache + '/osv-scanner'}


def command(ctx):
    # --no-resolve and offline databases keep dependency names on this machine; call analysis would run builds.
    return ['scan', 'source', '--recursive', '--no-ignore', '--allow-no-lockfiles', '--offline-vulnerabilities',
            '--download-offline-databases', '--no-resolve', '--config', ctx.config + '/osv-scanner.toml',
            '--format', 'json', '--output-file', ctx.output, ctx.source]


def level(members, score):
    """Keep the highest severity supplied by advisory labels or the group's CVSS score."""
    labels = [m.get('database_specific', {}).get('severity') for m in members if isinstance(m.get('database_specific'), dict)]
    labels = [label for label in labels if label in RANK]
    try:
        value = float(score)
    except (TypeError, ValueError):
        value = 0
    # Reject non-finite and out-of-range scores; they are not CVSS values.
    if 0 < value <= 10:
        labels.append('CRITICAL' if value >= 9 else 'HIGH' if value >= 7 else 'MEDIUM' if value >= 4 else 'LOW')
    return max(labels, key=RANK.index) if labels else None


def fixed_version(members, name, ecosystem):
    """Only an unambiguous fixed version; several candidates leave it empty."""
    fixes = {event['fixed'] for member in members for affected in member.get('affected') or []
             if isinstance(affected, dict) and affected.get('package', {}).get('name') == name
             and affected.get('package', {}).get('ecosystem') == ecosystem
             for span in affected.get('ranges') or [] for event in span.get('events') or []
             if isinstance(event, dict) and isinstance(event.get('fixed'), str)}
    return fixes.pop() if len(fixes) == 1 else ''


def parse(data, plugin, source):
    if not isinstance(data, dict) or not isinstance(data.get('results'), list):
        raise ValueError('Invalid OSV-Scanner report')
    records = []
    for result in data['results']:
        path = relative_path(result['source']['path'], source)
        for package in result['packages']:
            info = package['package']
            advisories = {v['id']: v for v in package.get('vulnerabilities') or []}
            for group in package.get('groups') or []:
                ids = group['ids']
                if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or not i for i in ids):
                    raise ValueError('OSV vulnerability group has no valid identifiers')
                aliases = group.get('aliases') or ids
                members = [advisories[i] for i in ids if i in advisories]
                cwe = sorted({c for m in members for c in (m.get('database_specific') or {}).get('cwe_ids') or []
                              if isinstance(c, str) and re.fullmatch(r'CWE-[1-9][0-9]{0,4}', c)})
                # One group is one vulnerability under several IDs; name it as the other SCA tools would.
                records.append(finding(plugin, canonical_advisory(sorted(ids)[0], aliases), path,
                                       severity(plugin, level(members, group.get('max_severity'))),
                                       package=info['name'], version=info['version'],
                                       fixed=fixed_version(members, info['name'], info.get('ecosystem')), cwe=cwe[:10]))
    return records
