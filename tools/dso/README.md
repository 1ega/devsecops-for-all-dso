# dso: repository scans, finding gates and baseline checks

A standard-library Python 3.10+ CLI for Linux/macOS. It runs reviewed scanners on
a private snapshot of the target, normalizes results, evaluates severity/delta
gates, and validates private company inventory/evidence/exception registers. The
[MCP server](../../mcp/dso/README.md) uses the same scanning core.

## Scan a project

Run from this kit checkout; the target is the application directory:

```bash
python3 tools/dso/dso.py doctor --engine docker
report_dir="$(mktemp -d)"
python3 tools/dso/dso.py scan repo ../your-project \
  --engine docker --project team/application --output "$report_dir/report.json"
python3 tools/dso/dso.py gate --input "$report_dir/report.json" --fail-on high
```

`--project` is required: use a stable ID shared by local and CI scans (in CI,
`owner/repository`). `scan` returns `0` for a completed scan even when it finds
vulnerabilities, and `2` for incomplete scans or invalid input; the report is
still written for diagnosis. **Use `gate` to enforce a policy.** `gate` returns
`0` for pass, `1` for blocking findings, and `2` for incomplete or incomparable
input. Interrupts (SIGINT/SIGTERM/SIGHUP) stop scanner processes and containers
and return `130`. Output files are atomically replaced with mode `0600`; the
output location is checked before scanning starts.

`doctor --engine docker` checks the daemon and whether each pinned image is
present locally (a scan pulls missing images). `doctor` for native checks the
detected version and path of each executable. Neither installs anything.

## How a scan works

DSO copies the target into a private temporary snapshot and scans only that copy:

- Every file must be readable. Unreadable files, symlinks, sockets/FIFOs, paths
  with control characters, files over 64 MiB, trees over 2 GiB or 100 000 files
  make the scan incomplete rather than silently smaller. Exclude reviewed paths
  explicitly with `--exclude path/inside/target` (repeatable; recorded in the
  report coverage).
- Directories named `.git`, `.venv`, `venv`, `__pycache__` and `node_modules`
  are never copied.
- Target ignore files (`.gitleaksignore`, `.semgrepignore`, `.gitignore`) are not
  copied, and Semgrep's built-in ignores and file-size limit are disabled. The
  target cannot hide files from the scan.
- Python files must parse with the runner's Python. Templates or legacy Python 2
  files make Semgrep coverage incomplete until excluded explicitly. Syntax newer
  than the runner's Python is also rejected, so run DSO with a current Python.

The default engine is `native`. Install the scanner versions pinned in
[plugins.json](plugins.json) (for example with [`mcp/dso/install.sh`](../../mcp/dso/README.md),
which verifies hashes), then use `doctor`. Version mismatches fail the scan.
Native scanners have the caller's permissions; Docker is preferred for untrusted
repositories. Environment variables prefixed `SEMGREP_`, `GITLEAKS_`, `TRIVY_` and
`GIT_` are cleared for scanners; normal proxy/certificate variables remain.
Native Trivy reuses `DSO_CACHE_DIR` when it is writable, otherwise it downloads
its database into the private run directory.

Docker is required for `--engine docker`; images are pinned by digest in
[plugins.json](plugins.json). Containers run as the caller's UID (root if DSO runs
as root) with a read-only root filesystem, all capabilities dropped,
`no-new-privileges`, 3 GiB memory and 256-process limits. Only the snapshot
(read-only) and a private work directory with copied trusted rules are mounted.
Plugins run without network unless the manifest marks them `network` (Trivy, for
its database download); those receive proxy variables and `SSL_CERT_FILE`. Before each scanner runs, a sentinel
check proves the daemon sees the same snapshot. Remote daemons, Docker-in-Docker
and socket-mounted CI jobs need identical `TMPDIR` paths on client and daemon,
otherwise the scan is incomplete with `mount_visibility`.

Choose a profile with `--profile` (default `ci-blocking`) and run only some of its
plugins with `--plugins gitleaks semgrep` (`--tools` is an alias). Set a per-plugin
limit with `--timeout 300` (1–1800 seconds). Missing executables, failed version
checks, timeouts, non-success exits, rate limiting, permission errors, full disks,
malformed/missing reports and Semgrep analysis errors mark the scan incomplete;
each failed run records an `error_code` and a safe description. Scanner
diagnostics are not stored because they can contain source text.

## Plugins and profiles

[plugins.json](plugins.json) is the single source of DSO scanner pins and metadata.
Each plugin names its tool, version, image digest, native install (release binary
with SHA256 per platform, or a pip package from the hash-locked requirements),
target types, category, network and credential needs, exit codes, severity
mapping, CWE, manual and playbook. Each profile names a target type and the
plugins it runs with their kit options, such as the Gitleaks config or the Semgrep
rule directories. `doctor` and `mcp/dso/install_scanners.py` read the same file,
and `tools/validation/check_repo.py` fails when a workflow, Dockerfile, manual,
requirements file or `tools/versions.json` pins a different version or digest.

Plugins only reference rules, policies and scanner configs in `rules/`,
`policies/` and `scanners/`; those packages carry no DSO metadata and keep their
own README with a command that works without DSO.

To add a plugin, write an adapter in [plugins/](plugins/__init__.py) (`OPTIONS`,
`policy_files`, `prepare`, `command`, `parse`), add its manifest entry, select it
in a profile, and add adapter tests with a finding fixture and a clean one. The
core runs, sandboxes, times out and validates every plugin the same way.

## Profile and coverage

The `ci-blocking` profile:

| Scanner | Scope | Severity mapping |
| --- | --- | --- |
| Gitleaks | Snapshot files with the imported default rules; inline allow comments, target ignore files and the upstream `gitleaks.toml` path allowlist disabled | All secret findings: high |
| Semgrep | The three local Python starter rules, strict analysis, `nosem` disabled, no ignore files or size limit | ERROR/HIGH high, CRITICAL critical, WARNING/MEDIUM medium, LOW low, INFO info; other values unknown |
| Trivy | Filesystem dependency vulnerabilities in offline mode (no Maven/registry lookups); empty explicit ignore/config files | Native severity; unsupported severity becomes unknown |

The starter rules are `ERROR`, so they block at the default `high` threshold.
This is not a full-history secret scan, general language SAST, image/IaC scan,
or proof of complete asset coverage. Semgrep can complete with zero applicable
Python files. Trivy can complete with no recognized dependency files; offline
mode cannot resolve remote parent POMs or transitive dependencies that are not
in a lock file.

## Baselines and gates

```bash
python3 tools/dso/dso.py gate --input "$report_dir/report.json" \
  --baseline /private/path/approved-baseline.json --fail-on high
```

Without a baseline, all findings at or above the threshold block. With one, only
new or severity-escalated findings block. Unknown severity always blocks, with or
without a baseline. Both reports must be complete and have the same project.
Other coverage differences (engine, tools, versions, policy digest, exclusions)
are listed in `coverage_changes` and still compared: a baseline only accepts
exact finding IDs, so a kit or tool update can make findings new but never hides
one. Gate output also lists `resolved` baseline IDs and `fix_changed` findings.
No baseline is implicitly generated or refreshed. Review a completed report and
store an approved copy through your team's protected process.

Finding IDs hash tool, rule, relative path, line, package, installed version and,
for secrets, a fingerprint of the matched value. They remain stable for
identical content across runs, engines and checkout roots. Moving source lines or
files creates new findings deliberately. Duplicate identities within a scanner
collapse to the highest severity (unknown wins). Findings from different tools
remain separate.

A baseline can waive existing high/critical findings: protect it and its selected
commit from untrusted PR changes. These JSON files are not signed evidence and
contain secret fingerprints, so keep them private. There is no automatic expiry
or suppression integration with `exceptions` yet.

The [report contract](../../reporting/dso-report.md) explains fields, semantics
and limits. For CI use the [GitHub Actions gate](../../integrations/github-actions/README.md)
or [GitLab gate](../../integrations/gitlab-ci/README.md).

## Company evidence commands

```bash
cp baseline/assessment.example.json /private/path/assessment.json
cp baseline/assets.example.csv /private/path/assets.csv
python3 tools/dso/dso.py inventory --input /private/path/assets.csv
python3 tools/dso/dso.py assess --input /private/path/assessment.json --all
python3 tools/dso/dso.py exceptions --input /private/path/exceptions.json
```

These validate owner-supplied evidence, not provider state. Refresh example dates
(UTC). Snapshots must be at most seven days old; implemented controls need an
owner, current review and nonempty evidence. Inventory CSV may have a UTF-8 BOM;
values are trimmed and case-insensitive for criticality/exposure; malformed
quoting and duplicate headers are input errors. Exceptions require an asset, rule,
owner, a different approver, reason, compensating control, ticket and a 1–90 day
expiry; IDs and tool/rule/asset scopes must be unique (case-insensitive). Expiry
today fails. Add `--format json` for machine output. Exit codes: 0 valid,
1 gaps/expired exceptions, 2 malformed input. See [company baseline](../../baseline/README.md).

## Tests and cleanup

```bash
python3 -m unittest discover -s tools/dso/tests -v
# Opt-in: real scanners, network/database downloads and synthetic fixtures.
python3 tools/dso/tests/smoke.py --engine docker
```

Unit tests cover adapters, multi-line and rotated secrets, deduplication,
delta/escalation and unknown-severity gates, coverage changes, snapshot rules
(ignore files, symlinks, special and unreadable files), incomplete scans,
timeouts, cancellation, diagnostics, private output and existing commands. The
real smoke test checks detections, blocking and clean fixes with the same runner;
it never executes application code. Delete private output reports when finished.
Snapshots, raw scanner reports and scanner temporary files are removed by the
runner, including after an interrupt. Keep real findings outside public git.
Original code is MIT licensed.
