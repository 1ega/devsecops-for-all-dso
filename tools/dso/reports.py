"""DSO report v3: finding identity, trusted references, validation and delta gates."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import inventory
import manifest
from manifest import SEVERITIES
import register
import runtime
from runtime import EXCLUDED, text

SCHEMA_VERSION = 3
REPORT_FIELDS = {'schema_version', 'project', 'target', 'created_at', 'coverage', 'input', 'complete', 'runs', 'findings'}
COVERAGE_FIELDS = {'profile', 'plugins', 'versions', 'engine', 'policy_digest', 'exclusions', 'default_exclusions'}
# Implemented scan targets; the manifest also names planned ones.
TARGETS = ('repo', 'image')
# A fetched tree records the public repository and commit it came from.
IMAGE_REFERENCE = re.compile(r'(?:[a-z0-9.-]+(?::[0-9]{1,5})?/)?[a-z0-9]+(?:[._/-][a-z0-9]+)*'
                             r'(?::[A-Za-z0-9_][A-Za-z0-9_.-]{0,127})?@sha256:[a-f0-9]{64}')
ORIGIN = re.compile(r'https://github\.com/[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}')
ADVISORIES = [(re.compile(r'CVE-[0-9]{4}-[0-9]{4,19}'), 'https://nvd.nist.gov/vuln/detail/{}'),
              (re.compile(r'GHSA(-[23456789cfghjmpqrvwx]{4}){3}'), 'https://github.com/advisories/{}'),
              (re.compile(r'(GO|PYSEC|RUSTSEC)-[0-9]{4}-[0-9]{1,7}'), 'https://osv.dev/vulnerability/{}')]
# Display and ranking order: what blocks first. Unknown severity always blocks.
ORDER = ('critical', 'high', 'unknown', 'medium', 'low', 'info')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def canonical_advisory(primary, aliases=()):
    """The ID other tools are likeliest to report: the primary when it is a CVE, else a CVE alias,
    else a GHSA, else the primary. Trivy already prefers CVE IDs, so the three SCA tools line up."""
    candidates = [primary, *sorted(a for a in aliases if isinstance(a, str) and a)]
    for pattern, _ in ADVISORIES[:2]:
        for candidate in candidates:
            if pattern.fullmatch(candidate):
                return candidate
    return primary


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
        if (previous is None or record['severity'] == 'unknown' or
                previous['severity'] != 'unknown' and SEVERITIES[record['severity']] > SEVERITIES[previous['severity']]):
            unique[record['id']] = record
    return sorted(unique.values(), key=lambda r: r['id'])


def package_key(name):
    """Tools spell one package differently: Maven group:artifact or artifact alone, case, PEP 503 separators."""
    return re.sub(r'[-_.]+', '-', name.rsplit(':', 1)[-1].lower())


def version_key(version):
    """Go module versions keep their v in Trivy and Grype but not in OSV-Scanner."""
    version = version.lower()
    return version[1:] if len(version) > 1 and version[0] == 'v' and version[1].isdigit() else version


def issue_key(f, image=False):
    """What makes two findings the same problem. A dependency issue is the advisory, package and
    version in one lockfile (an image has one package database, so its paths differ by tool and are
    ignored); secret findings on one line are one issue; anything else is an issue of its own."""
    if f['category'] == 'sca':
        return digest(['sca', f['rule_id'], package_key(f['package']), version_key(f['installed_version']),
                       '' if image else f['path']])
    if f['category'] == 'secret' and f['line']:
        return digest(['secret', f['path'], f['line']])
    return f['id']


def issues(findings, image=False):
    """Findings grouped across tools into issues: one thing to fix or to accept. Finding IDs are
    kept inside each issue; the report itself still lists every tool's findings."""
    groups = {}
    for f in findings:
        groups.setdefault(issue_key(f, image), []).append(f)
    result = []
    for key, members in groups.items():
        members.sort(key=lambda f: f['id'])
        severities = {f['severity'] for f in members}
        severity = 'unknown' if 'unknown' in severities else max(severities, key=SEVERITIES.get)
        named = max(members, key=lambda f: (len(f['package']), f['package']))
        links = []
        for f in members:
            links.extend(r for r in f['references'] if r not in links)
        links.sort(key=lambda r: r.startswith('https://cwe.mitre.org/'))
        result.append({'key': key, 'category': members[0]['category'], 'severity': severity,
                       'rules': sorted({f['rule_id'] for f in members}),
                       'paths': sorted({f['path'] for f in members}), 'line': members[0]['line'],
                       'package': named['package'], 'installed_version': named['installed_version'],
                       'fixed_versions': sorted({f['fixed_version'] for f in members if f['fixed_version']}),
                       'plugins': sorted({f['plugin'] for f in members}), 'findings': [f['id'] for f in members],
                       'cwe': sorted({c for f in members for c in f['cwe']}, key=lambda c: int(c[4:])),
                       'references': links})
    result.sort(key=lambda i: (ORDER.index(i['severity']), i['category'], i['paths'][0], i['line'], i['rules'][0]))
    return result


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
        valid = f['fingerprint'] and not packaged
    elif f['category'] == 'sast':
        valid = not f['fingerprint'] and f['line'] >= 1 and not packaged
    elif f['category'] == 'sca':
        valid = not f['fingerprint'] and f['line'] == 0 and f['package']
    elif f['category'] in ('iac', 'cicd'):
        valid = not f['fingerprint'] and not packaged
    elif f['category'] == 'malware':
        valid = not f['fingerprint'] and f['line'] == 0 and not packaged
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
        image = profile['target'] == 'image'
        if coverage['default_exclusions'] != ([] if image else sorted(EXCLUDED)):
            raise ValueError('Unrecognized default exclusions')
        if image and coverage['exclusions']:
            raise ValueError('Image scans have no exclusions')
        if not isinstance(coverage['exclusions'], list) or len(coverage['exclusions']) > 100:
            raise ValueError('Invalid exclusions')
        for value in coverage['exclusions']:
            if relative_path(value, Path('/unused')) != value or Path(value).is_absolute():
                raise ValueError('Invalid exclusion')
        if coverage['exclusions'] != sorted(set(coverage['exclusions'])):
            raise ValueError('Exclusions must be sorted and unique')
        evidence = report['input']
        if image:
            if (not isinstance(evidence, dict) or set(evidence) != {'reference'} or not isinstance(evidence['reference'], str)
                    or not IMAGE_REFERENCE.fullmatch(evidence['reference'])):
                raise ValueError('Image scans record the image reference pinned by digest')
        elif not isinstance(evidence, dict) or set(evidence) - {'origin', 'inventory'} != {'files', 'bytes', 'sha256'}:
            raise ValueError('Invalid snapshot evidence')
        if not image and 'origin' in evidence:
            origin = evidence['origin']
            if (not isinstance(origin, dict) or set(origin) != {'url', 'commit'} or not isinstance(origin['url'], str) or
                    not ORIGIN.fullmatch(origin['url']) or not isinstance(origin['commit'], str) or
                    not re.fullmatch('[a-f0-9]{40}|[a-f0-9]{64}', origin['commit'])):
                raise ValueError('Invalid source origin')
        if not image and any(type(evidence[k]) is not int or evidence[k] < 0 for k in ('files', 'bytes')):
            raise ValueError('Invalid snapshot counts')
        if not image and (not isinstance(evidence['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', evidence['sha256'])):
            raise ValueError('Invalid snapshot digest')
        if not image and report['complete'] and evidence['sha256'] == '0' * 64:
            raise ValueError('Complete scan has no snapshot evidence')
        if not image and 'inventory' in evidence:
            inventory.check(evidence['inventory'], evidence['files'], relative_path)
        if not isinstance(report['runs'], list) or sorted(r['plugin'] for r in report['runs']) != names:
            raise ValueError('Missing or duplicate scanner run')
        if any(r['status'] not in ('complete', 'error') for r in report['runs']):
            raise ValueError('Invalid run status')
        if report['complete'] != all(r['status'] == 'complete' for r in report['runs']):
            raise ValueError('Inconsistent scan completion')
        if not isinstance(report['findings'], list):
            raise ValueError('Invalid findings')
        if len(report['findings']) > runtime.MAX_FINDINGS:
            raise ValueError(f'Report has more than {runtime.MAX_FINDINGS} findings; raise max_findings in dso config or pass --max-findings')
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


GAP_REASONS = {'no_dependency_files': 'no lockfile in the snapshot, so dependencies were not checked',
               'unlocked_manifests': 'manifests without a lockfile beside them are skipped by the dependency scanners',
               'no_iac_files': 'no Dockerfile, Terraform, Kubernetes, Helm, Compose or CloudFormation file in the snapshot',
               'no_ci_files': 'no GitHub Actions, GitLab CI, Azure Pipelines or Tekton file in the snapshot',
               'no_source_files': 'no source file in a language DSO recognizes'}


def gaps(report):
    """Selected plugins that had nothing to check, from the snapshot inventory: a zero-finding
    run then means "nothing to look at", not "clean". Empty for images and for reports without
    an inventory."""
    stock = report['input'].get('inventory')
    if stock is None:
        return []
    by_category = {}
    for name in report['coverage']['plugins']:
        by_category.setdefault(manifest.plugin(name)['category'], []).append(name)
    found = []

    def gap(category, reason, paths=()):
        if category in by_category:
            found.append({'plugins': by_category[category], 'reason': reason, 'detail': GAP_REASONS[reason],
                          'paths': sorted(paths)})
    if not stock['dependency_files']:
        gap('sca', 'no_dependency_files')
    if stock['unlocked']:
        gap('sca', 'unlocked_manifests', [p for paths in stock['unlocked'].values() for p in paths])
    if not stock['iac_files']:
        gap('iac', 'no_iac_files')
    if not stock['ci_files']:
        gap('cicd', 'no_ci_files')
    if not stock['languages']:
        gap('sast', 'no_source_files')
    return found


def covers(options, before):
    """Profile options that keep at least the baseline's kit files and rule directories."""
    if options is None:
        return False
    return all(set(value) <= set(options.get(key) or []) if isinstance(value, list) else options.get(key) == value
               for key, value in before.items())


def narrowed(report, baseline):
    """Coverage the current scan lost against the baseline; findings there would vanish unseen."""
    current, previous = report['coverage'], baseline['coverage']
    lost = []
    if set(previous['plugins']) - set(current['plugins']):
        lost.append('coverage.plugins')
    if set(current['exclusions']) - set(previous['exclusions']):
        lost.append('coverage.exclusions')
    if current['profile'] != previous['profile']:
        now = manifest.profile(current['profile'])['plugins']
        before = manifest.profile(previous['profile'])['plugins']
        if not all(covers(now.get(plugin), before[plugin]) for plugin in previous['plugins'] if plugin in current['plugins']):
            lost.append('coverage.profile')
    return lost


def waive(report, entries, today=None):
    """What a register does to one report: active entries with the finding IDs they cover (a
    dependency entry covers its whole issue, whichever tool reported it), expired entries that
    would still match, entries that match nothing, and the covering entry per finding."""
    image = report['target']['type'] == 'image'
    members = {}
    for issue in issues(report['findings'], image):
        for member in issue['findings']:
            members[member] = issue['findings'] if issue['category'] == 'sca' else [member]
    applied, expired, unused, covered = [], [], [], {}
    for entry in entries:
        matched = sorted({member for f in report['findings'] if register.matches(entry, f, report['project'])
                          for member in members[f['id']]})
        record = {'id': entry['id'], 'expires_on': entry['expires_on'], 'findings': matched}
        if not register.active(entry, today):
            if matched:
                expired.append(record)
        elif matched:
            applied.append(record)
            for member in matched:
                covered.setdefault(member, entry['id'])
        else:
            unused.append(entry['id'])
    return {'applied': applied, 'expired': expired, 'unused': unused, 'covered': covered}


def gate(report, baseline=None, fail_on='high', exceptions=None):
    """exceptions: entries from register.load; an active entry stops its findings from blocking."""
    if fail_on not in SEVERITIES or fail_on == 'unknown':
        raise ValueError('Invalid severity threshold')
    validate_report(report)
    if baseline is not None:
        validate_report(baseline)
    waived = waive(report, exceptions) if exceptions is not None else None
    covered = waived['covered'] if waived else {}
    mismatch, changes = [], []
    if baseline is not None:
        mismatch = [k for k in ('project', 'target') if report[k] != baseline[k]]
        mismatch += narrowed(report, baseline) if not mismatch else []
        # Other coverage changes (versions, rules, the DSO code, added plugins, fewer exclusions)
        # can only make findings new, because a baseline accepts exact IDs. Report them instead of
        # failing every gate after a kit update.
        changes = ['coverage.' + k for k in report['coverage'] if report['coverage'][k] != baseline['coverage'][k]]
    incompatible = bool(mismatch)
    comparable = baseline is not None and not incompatible and baseline['complete']
    image = report['target']['type'] == 'image'
    previous = {f['id']: f for f in baseline['findings']} if comparable else {}
    # A baseline decision about a dependency is about the vulnerability, not about which scanner
    # saw it: the same advisory, package and version reported by another tool is accepted at the
    # severity the baseline accepted. Secrets never cross tools here, because their fingerprints
    # differ per tool and a rotated secret on the same line must stay new.
    accepted_issues = {i['key']: i['severity'] for i in issues(baseline['findings'], image)
                       if i['category'] == 'sca'} if comparable else {}

    def accepted(f):
        if f['id'] in previous:
            return previous[f['id']]['severity']
        return accepted_issues.get(issue_key(f, image)) if f['category'] == 'sca' else None

    def escalated(f):
        before = accepted(f)
        return before is None or f['severity'] == 'unknown' or before == 'unknown' or SEVERITIES[f['severity']] > SEVERITIES[before]
    current = {f['id']: f for f in report['findings']}
    new = [f for f in report['findings'] if escalated(f)]
    severe = [f for f in new if f['severity'] == 'unknown' or SEVERITIES[f['severity']] >= SEVERITIES[fail_on]]
    blocking = [f for f in severe if f['id'] not in covered]
    incomplete = not report['complete'] or (baseline is not None and not baseline['complete']) or incompatible
    if waived is not None:
        waived = {'applied': waived['applied'], 'expired': waived['expired'], 'unused': waived['unused'],
                  'waived': len(severe) - len(blocking)}
    return {'exit_code': 2 if incomplete else (1 if blocking else 0),
            'status': 'incomparable' if incompatible else ('incomplete' if incomplete else ('blocked' if blocking else 'passed')),
            'mismatch': mismatch, 'coverage_changes': changes,
            'new_or_escalated': len(new), 'existing': len(report['findings']) - len(new),
            'blocking': blocking, 'blocking_issues': issues(blocking, image), 'gaps': gaps(report),
            'exceptions': waived,
            'resolved': [i for i in previous if i not in current] if report['complete'] else [],
            'fix_changed': [f['id'] for f in report['findings'] if f['id'] in previous and f['fixed_version'] != previous[f['id']]['fixed_version']]}
