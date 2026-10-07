"""DSO report v3: finding identity, trusted references, validation and delta gates."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import manifest
from manifest import SEVERITIES
from runtime import EXCLUDED, text

SCHEMA_VERSION = 3
REPORT_FIELDS = {'schema_version', 'project', 'target', 'created_at', 'coverage', 'input', 'complete', 'runs', 'findings'}
COVERAGE_FIELDS = {'profile', 'plugins', 'versions', 'engine', 'policy_digest', 'exclusions', 'default_exclusions'}
# Implemented scan targets; the manifest also names planned ones.
TARGETS = ('repo',)
ADVISORIES = [(re.compile(r'CVE-[0-9]{4}-[0-9]{4,19}'), 'https://nvd.nist.gov/vuln/detail/{}'),
              (re.compile(r'GHSA(-[23456789cfghjmpqrvwx]{4}){3}'), 'https://github.com/advisories/{}'),
              (re.compile(r'(GO|PYSEC|RUSTSEC)-[0-9]{4}-[0-9]{1,7}'), 'https://osv.dev/vulnerability/{}')]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def relative_path(value, target):
    text(value, 'finding path', 4096)
    path = Path(value)
    if path.is_absolute():
        try:
            path = path.relative_to(target)
        except ValueError:
            raise ValueError('Finding path outside scan target') from None
    if '..' in path.parts or path.as_posix() in ('.', ''):
        raise ValueError('Finding path escapes scan target')
    return path.as_posix()


def severity(plugin, native=None):
    """Map a scanner's own severity through the manifest; anything unmapped is unknown."""
    rule = manifest.plugin(plugin)['severity']
    if 'fixed' in rule:
        return rule['fixed']
    return rule['map'].get(native, 'unknown') if isinstance(native, str) else 'unknown'


def references(rule, cwe):
    """Links built only from validated identifiers, never from scanner text."""
    links = [url.format(rule) for pattern, url in ADVISORIES if pattern.fullmatch(rule)]
    return links + [f'https://cwe.mitre.org/data/definitions/{c[4:]}.html' for c in cwe]


def finding(plugin, rule, path, severity, line=0, package='', version='', fixed='', fingerprint='', cwe=()):
    spec = manifest.plugin(plugin)
    text(rule, 'rule', 512)
    text(path, 'path', 4096)
    if type(line) is not int or line < 0:
        raise ValueError('Invalid finding line')
    for value in (package, version, fixed):
        text(value, 'package metadata', 2048, empty=True)
    if fingerprint and not re.fullmatch('[a-f0-9]{64}', fingerprint):
        raise ValueError('Invalid finding fingerprint')
    if not isinstance(cwe, (list, tuple)) or not all(isinstance(c, str) and manifest.CWE.fullmatch(c) for c in cwe):
        raise ValueError('Invalid finding CWE')
    cwe = sorted(set(spec['cwe']) | set(cwe), key=lambda c: int(c[4:]))
    if len(cwe) > 10:
        raise ValueError('Too many CWE IDs')
    severity = str(severity).lower()
    if severity not in SEVERITIES:
        severity = 'unknown'
    return {'id': digest([plugin, rule, path, line, package, version, fingerprint]),
            'plugin': plugin, 'category': spec['category'], 'rule_id': rule, 'path': path, 'line': line,
            'package': package, 'installed_version': version, 'fixed_version': fixed,
            'severity': severity, 'fingerprint': fingerprint, 'cwe': cwe, 'references': references(rule, cwe)}


def deduplicate(records):
    """Duplicate identities within one plugin collapse to the highest severity; unknown wins."""
    unique = {}
    for record in records:
        previous = unique.get(record['id'])
        if previous is None or record['severity'] == 'unknown' or SEVERITIES[record['severity']] > SEVERITIES[previous['severity']]:
            unique[record['id']] = record
    return sorted(unique.values(), key=lambda r: r['id'])


def selected_plugins(names, profile):
    available = manifest.profile(profile)['plugins']
    names = sorted(available) if names is None else names
    if not isinstance(names, list) or not names or any(not isinstance(n, str) or n not in available for n in names):
        raise ValueError(f'Select one or more plugins of profile {profile}: ' + ', '.join(sorted(available)))
    if len(names) != len(set(names)):
        raise ValueError('Duplicate plugin selection')
    return sorted(names)


def check_shape(f):
    """Each category has one location shape; anything else is a tampered or foreign report."""
    spec = manifest.plugin(f['plugin'])
    packaged = any(f[k] for k in ('package', 'installed_version', 'fixed_version'))
    if 'fixed' in spec['severity'] and f['severity'] != spec['severity']['fixed']:
        raise ValueError('Severity differs from the plugin manifest')
    if f['category'] == 'secret':
        valid = f['fingerprint'] and f['line'] >= 1 and not packaged
    elif f['category'] == 'sast':
        valid = not f['fingerprint'] and f['line'] >= 1 and not packaged
    elif f['category'] == 'sca':
        valid = not f['fingerprint'] and f['line'] == 0 and f['package']
    else:
        valid = False
    if not valid:
        raise ValueError(f'Invalid {f["category"]} finding')


def validate_report(report):
    """Validate a bounded v3 snapshot. Structural validity is not authenticity."""
    try:
        if isinstance(report, dict) and report.get('schema_version') == 2:
            raise ValueError('DSO report v2 is no longer accepted; scan again for a v3 report or baseline (finding IDs are unchanged)')
        if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
            raise ValueError('Unexpected report fields; a v3 report is required')
        if type(report['schema_version']) is not int or report['schema_version'] != SCHEMA_VERSION or type(report['complete']) is not bool:
            raise ValueError('Unsupported report')
        text(report['project'], 'project', 200)
        stamp = text(report['created_at'], 'timestamp', 40)
        if not re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|\+00:00)', stamp):
            raise ValueError('created_at must be a UTC timestamp')
        try:
            created = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid UTC timestamp') from None
        if created > datetime.now(timezone.utc):
            raise ValueError('Report timestamp is in the future')
        coverage = report['coverage']
        if not isinstance(coverage, dict) or set(coverage) != COVERAGE_FIELDS:
            raise ValueError('Unexpected coverage fields')
        profile = manifest.profile(coverage['profile'])
        if report['target'] != {'type': profile['target']} or profile['target'] not in TARGETS:
            raise ValueError('Target type differs from the profile')
        if not isinstance(coverage['plugins'], list):
            raise ValueError('coverage.plugins must be a list')
        names = selected_plugins(coverage['plugins'], coverage['profile'])
        if names != coverage['plugins']:
            raise ValueError('coverage.plugins must be sorted')
        if not isinstance(coverage['policy_digest'], str) or not re.fullmatch('[a-f0-9]{64}', coverage['policy_digest']) or coverage['policy_digest'] == '0' * 64:
            raise ValueError('Invalid policy digest')
        if coverage['engine'] not in ('native', 'docker'):
            raise ValueError('Unrecognized engine')
        if not isinstance(coverage['versions'], dict) or set(coverage['versions']) != set(names):
            raise ValueError('Invalid versions')
        if not all(isinstance(v, str) and re.fullmatch(r'\d+\.\d+\.\d+', v) for v in coverage['versions'].values()):
            raise ValueError('Invalid scanner versions')
        if coverage['default_exclusions'] != sorted(EXCLUDED):
            raise ValueError('Unrecognized default exclusions')
        if not isinstance(coverage['exclusions'], list) or len(coverage['exclusions']) > 100:
            raise ValueError('Invalid exclusions')
        for value in coverage['exclusions']:
            if relative_path(value, Path('/unused')) != value or Path(value).is_absolute():
                raise ValueError('Invalid exclusion')
        if coverage['exclusions'] != sorted(set(coverage['exclusions'])):
            raise ValueError('Exclusions must be sorted and unique')
        evidence = report['input']
        if not isinstance(evidence, dict) or set(evidence) != {'files', 'bytes', 'sha256'}:
            raise ValueError('Invalid snapshot evidence')
        if any(type(evidence[k]) is not int or evidence[k] < 0 for k in ('files', 'bytes')):
            raise ValueError('Invalid snapshot counts')
        if not isinstance(evidence['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', evidence['sha256']):
            raise ValueError('Invalid snapshot digest')
        if report['complete'] and evidence['sha256'] == '0' * 64:
            raise ValueError('Complete scan has no snapshot evidence')
        if not isinstance(report['runs'], list) or sorted(r['plugin'] for r in report['runs']) != names:
            raise ValueError('Missing or duplicate scanner run')
        if any(r['status'] not in ('complete', 'error') for r in report['runs']):
            raise ValueError('Invalid run status')
        if report['complete'] != all(r['status'] == 'complete' for r in report['runs']):
            raise ValueError('Inconsistent scan completion')
        if not isinstance(report['findings'], list) or len(report['findings']) > 50000:
            raise ValueError('Invalid or excessive findings')
        seen = set()
        for f in report['findings']:
            if f['plugin'] not in names or f['severity'] not in SEVERITIES:
                raise ValueError('Invalid finding plugin or severity')
            if Path(f['path']).is_absolute():
                raise ValueError('Absolute finding path')
            expected = finding(f['plugin'], f['rule_id'], relative_path(f['path'], Path('/unused')), f['severity'], f['line'],
                               f['package'], f['installed_version'], f['fixed_version'], f['fingerprint'], f['cwe'])
            if f != expected or f['id'] in seen:
                raise ValueError('Invalid or duplicate finding')
            check_shape(f)
            seen.add(f['id'])
        if [f['id'] for f in report['findings']] != sorted(seen):
            raise ValueError('Findings must be sorted')
        for run in report['runs']:
            required = {'plugin', 'status', 'finding_count', 'exit_code'}
            expected_fields = required if run['status'] == 'complete' else required | {'error_code', 'error'}
            if set(run) != expected_fields:
                raise ValueError('Unexpected scanner run fields')
            if type(run['finding_count']) is not int or run['finding_count'] != sum(f['plugin'] == run['plugin'] for f in report['findings']):
                raise ValueError('Inconsistent finding count')
            code = run['exit_code']
            if code is not None and (type(code) is not int or not -255 <= code <= 255):
                raise ValueError('Invalid scanner exit code')
            if run['status'] == 'complete':
                codes = manifest.plugin(run['plugin'])['exit_codes']
                if code != (codes['findings'] if run['finding_count'] else codes['clean']):
                    raise ValueError('Completed run contradicts scanner exit code')
            else:
                text(run['error_code'], 'error code', 64)
                text(run['error'], 'error description', 512)
                if run['finding_count']:
                    raise ValueError('Incomplete scanner cannot contribute normalized findings')
    except (KeyError, TypeError, AttributeError, RecursionError) as exc:
        raise ValueError('Malformed DSO report') from exc
    return report


def gate(report, baseline=None, fail_on='high'):
    if fail_on not in SEVERITIES or fail_on == 'unknown':
        raise ValueError('Invalid severity threshold')
    validate_report(report)
    if baseline is not None:
        validate_report(baseline)
    mismatch, changes = [], []
    if baseline is not None:
        mismatch = [k for k in ('project', 'target') if report[k] != baseline[k]]
        # A baseline only accepts exact finding IDs, so a kit/policy/tool change can
        # only turn accepted findings into new ones. Report it instead of failing every MR.
        changes = ['coverage.' + k for k in report['coverage'] if report['coverage'][k] != baseline['coverage'][k]]
    comparable = baseline is not None and not mismatch and baseline['complete']
    previous = {f['id']: f for f in baseline['findings']} if comparable else {}
    current = {f['id']: f for f in report['findings']}
    new = [f for f in report['findings'] if f['id'] not in previous or f['severity'] == 'unknown' or
           previous[f['id']]['severity'] == 'unknown' or SEVERITIES[f['severity']] > SEVERITIES[previous[f['id']]['severity']]]
    blocking = [f for f in new if f['severity'] == 'unknown' or SEVERITIES[f['severity']] >= SEVERITIES[fail_on]]
    incomplete = not report['complete'] or (baseline is not None and not baseline['complete']) or bool(mismatch)
    return {'exit_code': 2 if incomplete else (1 if blocking else 0),
            'status': 'incomparable' if mismatch else ('incomplete' if incomplete else ('blocked' if blocking else 'passed')),
            'mismatch': mismatch, 'coverage_changes': changes,
            'new_or_escalated': len(new), 'existing': len(report['findings']) - len(new),
            'blocking': blocking,
            'resolved': [i for i in previous if i not in current] if report['complete'] else [],
            'fix_changed': [f['id'] for f in report['findings'] if f['id'] in previous and f['fixed_version'] != previous[f['id']]['fixed_version']]}
