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
| `target.type` | What was scanned; the profile decides it: `repo` or `image` |
| `created_at` | UTC timestamp (`Z` or `+00:00`), not in the future |
| `coverage.profile` | Manifest profile, for example `ci-blocking` |
| `coverage.plugins` | Sorted, unique plugin selection from that profile |
| `coverage.versions` | Reviewed scanner version per plugin (`X.Y.Z`) |
| `coverage.engine` | `native` or `docker` |
| `coverage.policy_digest` | SHA256 of the profile ID, the manifest, the DSO core, each selected adapter and every kit file the profile hands to a scanner (Gitleaks config, Semgrep rules) |
| `coverage.exclusions` | Sorted reviewer-supplied target-relative exclusions; empty for images |
| `coverage.default_exclusions` | Directory names never copied: `.git`, `.venv`, `venv`, `__pycache__`, `node_modules`; empty for images |
| `input` | Snapshot evidence: `files`, `bytes` and a SHA256 manifest of relative paths and contents; for a fetched repository also `origin` with its `url` (`https://github.com/OWNER/REPO`) and exact `commit`; and `inventory`, what the snapshot contained (below). An image scan records only `reference`, the image pinned by digest |
| `complete` | Boolean: every selected plugin completed |
| `runs` | One entry per plugin: `plugin`, `status`, `finding_count`, `exit_code`; errors add `error_code`/`error`. A partial Semgrep run adds target-relative `incomplete_files`, keeps its findings and makes the scan incomplete |
| `findings` | Normalized, deduplicated findings sorted by ID |

Every finding has `id`, `plugin`, `category`, `rule_id`, `path`, `line`,
`package`, `installed_version`, `fixed_version`, `severity`, `fingerprint`, `cwe`
and `references`. Empty strings and line 0 mean "not applicable". Severity is one
of info, low, medium, high, critical, unknown. Paths are target-relative; Trivy
target labels may include its ecosystem label. IDs are SHA256 of the JSON tuple
`[plugin, rule_id, path, line, package, installed_version, fingerprint]` with
sorted keys, compact separators and Python's default ASCII escaping.

`category` is the plugin's category from the manifest. Each category has one
shape: `secret` needs a fingerprint, `sast` a line and no package, `sca` a package
and line 0, `iac` and `cicd` no package or fingerprint, `malware` neither and line
0. A plugin with a fixed severity (Gitleaks, TruffleHog, YARA: high) cannot report
another one.

`cwe` lists sorted `CWE-N` IDs: the plugin's own (secret scanners: CWE-798, YARA:
CWE-506), the `cwe` metadata of the trusted Semgrep rule, and the CWE IDs of Trivy,
Grype and OSV advisories, each checked against
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

## Inventory and gaps

`input.inventory` records what DSO itself found in the snapshot, by file name with
a small content sniff for YAML and JSON, so that a run with no findings can be told
from a run that had nothing to check. It never comes from a scanner.

| Field | Content |
|---|---|
| `languages` | Source files per recognized language (python, javascript, typescript, go, java, kotlin, swift, objective-c, c, cpp, csharp, ruby, php, rust, scala, shell, dart) |
| `dependency_files` | Lockfiles and manifests the dependency scanners read, per ecosystem (pip, npm, go, maven, gradle, rubygems, cargo, composer, nuget, pub, cocoapods, swift, hex, conan): sorted relative paths, at most 100 per ecosystem |
| `unlocked` | Manifests with no lockfile beside them (`package.json` without a lock, `pyproject.toml` without `poetry.lock`, `uv.lock`, `pdm.lock` or `requirements.txt`, `Gemfile`, `Cargo.toml`, `composer.json`, `build.gradle`, `pubspec.yaml`, `Podfile`, `mix.exs`), per ecosystem. The scanners skip these |
| `iac_files` | Counts per kind: dockerfile, terraform, kubernetes (YAML with `apiVersion` and `kind`), helm (`Chart.yaml`), compose, cloudformation |
| `ci_files` | Counts per kind: github-actions, gitlab-ci, azure-pipelines, tekton |

The validator checks every key, count and path. Reports written before the
inventory existed have no `input.inventory` and still validate.

From the inventory and the selected plugins the gate derives `gaps`: plugins that
ran over nothing they could check. Each gap names its `plugins`, a `reason`
(`no_dependency_files`, `unlocked_manifests` with the `paths`, `no_iac_files`,
`no_ci_files`, `no_source_files`) and a fixed `detail` sentence. A gap does not
change the exit code; it is shown beside the result so that "0 findings" is read
correctly. Images have no inventory and no gaps.

## Issues

Several scanners report the same problem; the report keeps every tool's finding
and DSO derives *issues* from them when it shows or gates a report. Issues are
never stored, so a report cannot carry a contradictory grouping. An issue is the
set of findings with one key:

| Category | Issue key |
|---|---|
| `sca` | `rule_id`, package name and installed version, plus the lockfile path for repositories. Package names compare case-insensitively with `-`, `_` and `.` folded and a Maven `group:` prefix dropped; a leading `v` in a version is dropped. Image scans ignore the path, because Trivy names the OS package database `os/<distribution>` and Grype names the file |
| `secret` | path and line, when the line is known; the fingerprints differ per tool and are not compared |
| anything else | the finding itself |

Grype and OSV-Scanner name an advisory the way Trivy does: a CVE when the advisory
has one (Grype's related records, OSV's group aliases), otherwise its GHSA, so the
three tools produce the same `rule_id` for one vulnerability.

An issue carries `key` (SHA256 of the key tuple), `category`, `severity` (the
highest of its findings; unknown wins), `rules`, `paths`, `line`, `package`,
`installed_version`, `fixed_versions`, `plugins`, `findings` (the member IDs),
`cwe` and `references` (unions), and lists are sorted. Issues are ranked critical,
high, unknown, medium, low, info, then by category, path, line and rule. The gate
result lists `blocking_issues` beside `blocking`; the MCP server pages either view.

A baseline accepts a dependency issue whichever tool reports it, at the severity it
accepted, so adding a scanner does not re-block vulnerabilities a team already
decided on. Secrets are accepted only by exact finding ID.

## Gate output

`dso gate` prints `exit_code` (0 passed, 1 blocked, 2 incomplete or
incomparable), `status`, `mismatch` and `coverage_changes` against the baseline,
the counts `new_or_escalated` and `existing`, `blocking` (findings), the same
grouped as `blocking_issues`, `gaps`, `resolved` baseline IDs and `fix_changed`
IDs. With `--exceptions` it adds `exceptions`: `applied` entries with the finding
IDs each one covers and its `expires_on`, `expired` entries that findings still
match, `unused` entry IDs, and `waived`, how many findings would have blocked
without the register. Without a register `exceptions` is null. An entry covers a
finding when its `tool` is the plugin or `*`, its `rule_id` is the finding's and
its `asset_id` is the project or `*`; a dependency entry covers the whole issue.

The validator checks field sets, types, lengths, control characters, IDs and
ordering, duplicate identities, per-plugin counts, scanner exit codes from the
manifest against run status, category shapes, CWE and reference derivation, the
profile, its target, default exclusions and snapshot evidence. A valid incomplete
report is retained for diagnosis but cannot pass a gate. Structural validity is
not authenticity: reports and baselines must come from trusted execution and
storage. Database updates can legitimately add findings for unchanged
dependencies. Source line moves create new IDs.

Scanner reports and saved DSO JSON default to a 20 MiB limit, configurable with
`--max-report-mb`, `DSO_MAX_REPORT_MB` or `max_report_mb` in DSO config; a scan
may contain at most 50,000 normalized findings by default, configurable with
`--max-findings`, `DSO_MAX_FINDINGS` or `max_findings`. Use the same raised limits
to read or gate a large report. Exceeding a scanner limit marks that plugin
incomplete with `error_code: report_limit`. Exceeding the saved JSON limit fails
the write without replacing an existing report. Split the target or select
fewer plugins instead of treating a truncated report as a complete scan.

Gate output contains `exit_code` (0 pass, 1 blocking, 2 incomplete or
incomparable), `status`, `mismatch`, `coverage_changes`, `new_or_escalated`,
`existing`, `blocking`, `resolved` and `fix_changed`. Blocking findings are
listed even for incomplete scans. A baseline must have the same `project` and
`target`, and the scan must not cover less: a missing baseline plugin, an added
exclusion or a profile that drops the baseline's kit files or rule directories
makes it incomparable (exit 2), named in `mismatch` as `coverage.plugins`,
`coverage.exclusions` or `coverage.profile`. Other differences (versions, policy
digest, added plugins, removed exclusions, engine) are listed in
`coverage_changes` and stay comparable, because a baseline only accepts exact
finding IDs. Unknown severity blocks at any
threshold, with or without a baseline. Existing findings are not closed in any
external system; DefectDojo lifecycle integration is future work.
