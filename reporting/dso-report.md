# DSO repository report v3

Produced by [dso scan repo](../tools/dso/README.md) and the
[MCP tool](../mcp/dso/README.md). `tools/dso/reports.py:validate_report` is the
runtime validator used by the CLI and MCP gate. Plugins, profiles, categories and
severity mappings come from the [plugin manifest](../tools/dso/plugins.json). This
scan snapshot is separate from the [finding lifecycle record](finding.example.json),
which adds human ownership, SLA, tickets and risk decisions.

Version 2 reports and baselines are rejected with a message to scan again. Finding
IDs did not change between v2 and v3, so a new baseline accepts exactly the same
findings as the old one.

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer 3 |
| `project` | Required explicit project ID, at most 200 characters |
| `target.type` | What was scanned; the profile decides it. Currently always `repo` |
| `created_at` | UTC timestamp (`Z` or `+00:00`), not in the future |
| `coverage.profile` | Manifest profile, for example `ci-blocking` |
| `coverage.plugins` | Sorted, unique plugin selection from that profile |
| `coverage.versions` | Reviewed scanner version per plugin (`X.Y.Z`) |
| `coverage.engine` | `native` or `docker` |
| `coverage.policy_digest` | SHA256 of the profile ID, the manifest, the DSO core, each selected adapter and every kit file the profile hands to a scanner (Gitleaks config, Semgrep rules) |
| `coverage.exclusions` | Sorted reviewer-supplied target-relative exclusions |
| `coverage.default_exclusions` | Directory names never copied: `.git`, `.venv`, `venv`, `__pycache__`, `node_modules` |
| `input` | Snapshot evidence: `files`, `bytes` and a SHA256 manifest of relative paths and contents |
| `complete` | Boolean: every selected plugin completed |
| `runs` | One entry per plugin: `plugin`, `status`, `finding_count`, `exit_code`, plus `error_code`/`error` when it failed |
| `findings` | Normalized, deduplicated findings sorted by ID |

Every finding has `id`, `plugin`, `category`, `rule_id`, `path`, `line`,
`package`, `installed_version`, `fixed_version`, `severity`, `fingerprint`, `cwe`
and `references`. Empty strings and line 0 mean "not applicable". Severity is one
of info, low, medium, high, critical, unknown. Paths are target-relative; Trivy
target labels may include its ecosystem label. IDs are SHA256 of the JSON tuple
`[plugin, rule_id, path, line, package, installed_version, fingerprint]` with
sorted keys, compact separators and Python's default ASCII escaping.

`category` is the plugin's category from the manifest. Each category has one
shape: `secret` needs a fingerprint and a line, `sast` a line and no package,
`sca` a package and line 0. A plugin with a fixed severity (Gitleaks: high) cannot
report another one.

`cwe` lists sorted `CWE-N` IDs: the plugin's own (Gitleaks: CWE-798), the `cwe`
metadata of the trusted Semgrep rule, and Trivy's CWE IDs, each checked against
`CWE-[1-9][0-9]{0,4}`. `references` is never copied from a scanner. It is derived
from the rule ID and `cwe` only: a CVE links to NVD, a GHSA to GitHub Advisories,
GO/PYSEC/RUSTSEC IDs to OSV, each CWE to MITRE. The validator recomputes it, so an
edited report cannot carry other links.

Secret findings carry `fingerprint`: SHA256 of a DSO domain prefix, the rule ID
and the matched secret. A rotated or replaced secret at the same location is
therefore a new finding. The value itself is never stored, but a weak secret can
be confirmed by guessing, so treat reports and baselines as confidential. Other
categories leave `fingerprint` empty. Reports contain no source snippets, raw
matches or scanner messages. Locations and package identifiers are still private
data.

The validator checks field sets, types, lengths, control characters, IDs and
ordering, duplicate identities, per-plugin counts, scanner exit codes from the
manifest against run status, category shapes, CWE and reference derivation, the
profile, its target, default exclusions and snapshot evidence. A valid incomplete
report is retained for diagnosis but cannot pass a gate. Structural validity is
not authenticity: reports and baselines must come from trusted execution and
storage. Database updates can legitimately add findings for unchanged
dependencies. Source line moves create new IDs.

Gate output contains `exit_code` (0 pass, 1 blocking, 2 incomplete or
incomparable), `status`, `mismatch`, `coverage_changes`, `new_or_escalated`,
`existing`, `blocking`, `resolved` and `fix_changed`. Blocking findings are
listed even for incomplete scans. A baseline must have the same `project` and
`target`; other coverage differences (profile, engine, plugin selection, versions,
policy, exclusions) are reported in `coverage_changes` but still compared, because
a baseline only accepts exact finding IDs. Unknown severity blocks at any
threshold, with or without a baseline. Existing findings are not closed in any
external system; DefectDojo lifecycle integration is future work.
