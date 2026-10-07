# dso: repository scans, finding gates and baseline checks

A standard-library Python 3.10+ CLI for Linux/macOS. It runs reviewed scanners on
a private snapshot of the target, normalizes results, evaluates severity/delta
gates, and validates private company inventory/evidence/exception registers. The
[MCP server](../../mcp/dso/README.md) uses the same scanning core.

## Quick start

```bash
dso                                                   # menu: Enter, then paste what to scan
dso scan https://github.com/we45/Vulnerable-Flask-App
dso scan ~/src/app
dso scan alpine:3.20
```

> **Disk and download size.** The `audit` and `image` profiles check
> dependencies against local vulnerability databases, so nothing about your code
> leaves the machine, but they are large: about 565 MB to download on the first
> scan and about 4.9 GB on disk (Trivy 1.4 GB, Grype 3.2 GB, OSV about 250 MB per
> scanned ecosystem; scanning `.jar` files adds the Trivy Java DB, about 1 GB).
> They are cached in `~/.cache/dso` and refreshed about once a day. `ci-blocking`
> needs only the Trivy DB. `dso doctor --profile audit` shows what is cached, and
> every scan says what it is about to download.

For an audit with one dependency scanner and a smaller database footprint, select
Trivy and the other audit plugins explicitly:

```bash
dso scan repo . --project team/app --profile audit \
  --plugins gitleaks trufflehog semgrep trivy trivy-config poutine yara \
  --output /private/path/app.json
dso scan alpine:3.20 --plugins trivy-image
```

These selections omit Grype's roughly 3.2 GB database; the repository command
also omits OSV's local databases. They retain Trivy's dependency checks but lose
the other scanners' independent SCA results. To avoid vulnerability databases
entirely, omit Trivy too; that also removes dependency vulnerability coverage.

`dso scan TARGET` works out what TARGET is: a folder, a single file, a public
GitHub repository or account URL, or a container image (a tag is pinned to its
digest with an anonymous registry request). It then picks the project ID, the
most complete profile whose scanners are all installed (`audit` after
`mcp/dso/install.sh`, otherwise `ci-blocking`), and a report file in
`~/.dso/reports/`. Every option of the explicit commands below still works and
overrides those choices.

## Settings

```bash
dso config          # every setting, its value and where it came from
dso config init     # write ~/.dso/config.json with the defaults spelled out
```

| Setting | Default | Environment variable | Meaning |
| --- | --- | --- | --- |
| `reports_dir` | `~/.dso/reports` | `DSO_REPORTS_DIR` | where the menu and `dso scan TARGET` save reports |
| `cache_dir` | auto (`~/.cache/dso`) | `DSO_CACHE_DIR` | vulnerability database cache |
| `engine` | `native` | | default engine for scans |
| `profile` | auto | | default repository profile; auto picks the most complete one whose scanners are installed |
| `timeout` | 300 | | seconds per plugin, 1-1800 |
| `max_report_mb` | 20 | `DSO_MAX_REPORT_MB` | largest report DSO writes or reads, 20-1024 MiB |
| `max_findings` | 50000 | `DSO_MAX_FINDINGS` | most findings in one report, 1000-1000000 |

Precedence is command-line option (`--engine`, `--timeout`, `--max-report-mb`,
`--max-findings`) over environment variable over file over default. The file is
`~/.dso/config.json`, or the path in `DSO_CONFIG`; it must be a regular file
owned by you that nobody else can write, and it is never read from a scanned
directory, so a target cannot change its own limits or exclusions.

The two limits bound every report DSO writes or reads, including baselines, so a
report written with a raised limit needs the same limit where it is gated (in CI,
pass `--max-report-mb` or set `DSO_MAX_REPORT_MB`). Responses from GitHub and
registries stay bounded at 20 MiB whatever the settings say. A large monorepo
with the `audit` profile is the usual reason to raise them: three dependency
scanners report the same vulnerability under different IDs.

The default 20 MiB `max_report_mb` applies to each scanner's output (including
Trivy config) and the saved DSO report; `max_findings` defaults to 50,000. For a
larger scan, pass the same raised limits to both `scan` and `gate`, or set
`DSO_MAX_REPORT_MB` and `DSO_MAX_FINDINGS` for both commands:

```bash
report="$(mktemp -d)/report.json"
dso scan repo . --project team/app --engine docker --output "$report" \
  --max-report-mb 256 --max-findings 200000
dso gate --input "$report" --max-report-mb 256 --max-findings 200000
```

If a snapshot contains Python files that cannot be parsed by modern Python (for
example Python 2 scripts), Semgrep scans the other files from a filtered private
copy. Semgrep can also report a timeout or parse error for a particular file.
In either case, its run is marked `partial` with the exact `incomplete_files`;
its findings from other files are kept, but the report is incomplete and the
gate returns `2` until those files are reviewed or explicitly excluded. Other
plugins still see the original snapshot.

## Scan a project

Run from this kit checkout; the target is the application directory:

```bash
python3 tools/dso/dso.py doctor --engine docker
report_dir="$(mktemp -d)"
python3 tools/dso/dso.py scan repo ../your-project \
  --engine docker --project team/application --output "$report_dir/report.json"
python3 tools/dso/dso.py gate --input "$report_dir/report.json" --fail-on high
```

[`mcp/dso/install.sh`](../../mcp/dso/README.md) also installs a `dso` command that
runs this CLI with the pinned native scanners, so `dso doctor`, `dso scan repo ...`
and `dso gate ...` work from any directory once it is on your `PATH`.

Run `dso` without arguments in a terminal for an interactive menu: it asks for the
directory, project ID, engine and report file (default `~/.dso/reports/`, or
`DSO_REPORTS_DIR`), shows the command it runs, then a live step list and the
findings. `dso --help` and `dso <command> --help` describe every option.

`scan`, `gate` and `doctor` print readable text when stdout is a terminal and JSON
otherwise, so scripts and CI keep the JSON; force either with `--format text` or
`--format json`. Text output only shows report, gate and manifest fields, escapes
paths and package names, and honours `NO_COLOR`.

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

## Scan public GitHub repositories

```bash
dso scan repo https://github.com/owner/repo --output ~/.dso/reports/repo.json
dso scan org https://github.com/owner --output-dir ~/.dso/reports/owner --limit 20
```

`scan repo` also takes a repository URL; `--project` then defaults to
`github.com/OWNER/REPO` and the report's `input.origin` records the URL and the
exact commit. `scan org` lists the public repositories of an organization or user
(forks and archived ones only with `--include-forks`/`--include-archived`), scans
each, and writes `repos/NAME.json` plus `summary.json` into `--output-dir` (mode
0700). The interactive menu offers the same three sources.

Fetching needs `git` and the network, and is deliberately narrow:

- Public repositories only, anonymously over HTTPS. System and user git
  configuration, credential helpers and prompts are disabled, so no credential is
  sent. Anonymous GitHub API use allows 60 requests per hour. `scan org` uses
  the account request and paginated listings (one per 100 repositories), then
  reuses that metadata when fetching each repository. A direct `scan repo`
  uses one repository request.
- A shallow bare clone of the default branch; the tree is written from git
  objects without a checkout. No hook, filter, LFS, attribute (including
  `export-ignore`) or submodule runs, and nothing from the repository executes.
- Symlinks and submodules have no content of their own and are not scanned; LFS
  files are scanned as their pointer files.
- Paths are checked like local files. Two paths that collide on this filesystem
  (names differing only in case on macOS) make the fetch fail instead of dropping
  a file. The fetched tree is deleted after the scan.

## Scan a container image

```bash
dso scan image docker.io/library/alpine:3.20@sha256:<digest> --output ~/.dso/reports/alpine.json
```

The `image` profile runs Trivy and Grype against an image pinned by digest (find it
with `docker buildx imagetools inspect NAME:TAG`). Both pull the image straight from
its registry with an empty Docker configuration, so only public images work and
no local Docker daemon is needed. `--project` defaults to the image name without
tag or digest, so reports of rebuilt images compare against one baseline. OS
package findings use the path `os/<distribution>` instead of the image name, for
the same reason. The report records the exact reference in `input.reference`.

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
- DSO records what the snapshot contained (`input.inventory`: source languages,
  lockfiles per ecosystem, manifests without a lockfile, IaC and CI files) and
  the terminal and gate list `gaps`: plugins that had nothing to check, such as
  the dependency scanners in a tree with a `package.json` but no lockfile. A
  zero-finding run is then not mistaken for a clean one.

The default engine is `native`. Install the scanner versions pinned in
[plugins.json](plugins.json) (for example with [`mcp/dso/install.sh`](../../mcp/dso/README.md),
which verifies hashes), then use `doctor`. Version mismatches fail the scan.
Native scanners have the caller's permissions; Docker is preferred for untrusted
repositories. Environment variables prefixed with any manifest tool name (such as
`SEMGREP_`, `TRIVY_`, `GRYPE_`, `TRUFFLEHOG_`) and `GIT_` are cleared for scanners;
normal proxy/certificate variables remain, and Trivy and Grype get an empty Docker
configuration so no registry credential helper is involved.

Vulnerability databases are cached in `DSO_CACHE_DIR` when it is set and writable,
otherwise in `~/.cache/dso` (or `$XDG_CACHE_HOME/dso`, mode 0700, owned by you),
otherwise in the private run directory. The manifest records each database's
approximate download and disk size (`database` in [plugins.json](plugins.json));
see the size note at the top. With `--engine docker`, the same persistent cache
is bind-mounted at `/cache`; the Docker daemon must be able to access its host
path. Without a writable persistent cache, the run uses a temporary cache.
A warm `audit` scan of a small project takes
about 40 seconds; the first one about 100.

Docker is required for `--engine docker`; images are pinned by digest in
[plugins.json](plugins.json). Containers run as the caller's UID (root if DSO runs
as root) with a read-only root filesystem, all capabilities dropped,
`no-new-privileges`, 3 GiB memory and 256-process limits. The snapshot
(read-only), a private work directory with copied trusted rules and, when
available, the persistent database cache are mounted.
Plugins run without network unless the manifest marks them `network` (Trivy,
Grype and OSV-Scanner, for their database downloads); those receive proxy variables
and `SSL_CERT_FILE`. Before the plugins run, a sentinel check with the pinned
`probe_image` (BusyBox) proves the daemon sees the same snapshot. Probe files use
unique names and are removed before scanning; existing source files are preserved. Remote daemons,
Docker-in-Docker and socket-mounted CI jobs need identical `TMPDIR` paths on client
and daemon, otherwise the scan is incomplete with `mount_visibility`. YARA-X has no
reviewed upstream image, so the `yara` plugin runs only with `--engine native`
(`no_image` otherwise).

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

## Profiles and coverage

`dso doctor --profile audit` checks every scanner a profile needs.

The `ci-blocking` profile (default; fast, for merge request gates):

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

The `audit` profile runs every repository plugin, for scheduled scans and manual
audits rather than blocking merge requests:

| Plugin | Category | Scope and limits |
| --- | --- | --- |
| Gitleaks, Trivy | secret, sca | As in `ci-blocking` |
| TruffleHog | secret | Every detector over the snapshot with `--no-ignore-tag`; no verification, because that sends each secret to its provider. Severity high |
| Semgrep | sast | Python starter, Trail of Bits (AGPL-3.0), elttam without its 12 incompatible Java rules and one crashing JSP join rule in Semgrep 1.179.0, and the mobile rules |
| Grype | sca | The snapshot directory with an explicit configuration; database download needs the network |
| OSV-Scanner | sca | Lockfiles checked against downloaded OSV databases with `--no-resolve`: dependency names are never sent. An explicit empty config overrides `osv-scanner.toml` in the target. Call analysis is never enabled, because it runs builds |
| Trivy config | iac | Dockerfile, Terraform, Kubernetes, Helm and other IaC with the checks embedded in the pinned version. Trivy still honours inline `trivy:ignore` comments in the target |
| poutine | cicd | GitHub Actions, GitLab CI, Azure Pipelines and Tekton files with an explicit empty config; no network |
| YARA-X | malware | `signature-base`, `reversinglabs`, `bartblaze` and `elastic` rules over every file; any read error makes the run incomplete. Severity high. Native engine only |

OSV severity takes the highest of the advisory labels and the group's numeric
CVSS score, so a lower label cannot hide a higher score. Invalid or unavailable
scores without a recognized label remain `unknown` and block the gate.

The three dependency scanners overlap on purpose. Each keeps its own finding in the
report, named by the ID the tools share (a CVE when the advisory has one, else its
GHSA), and the terminal, the gate's `blocking_issues` and the MCP `issues` view
group them into issues: one advisory in one package version of one lockfile is
one issue however many tools saw it, and the same secret line found by Gitleaks
and TruffleHog is one issue too. Finding IDs are never merged; an issue lists them.
YARA
rules are written for binaries, so source trees, test fixtures and security tooling
(including this kit's own `rules/yara/`) produce false positives; exclude them with
`--exclude`. The `signature-base` rules (DRL 1.1) ask you to keep their author and
license reference when sharing match reports, and the `elastic` rules (Elastic
License 2.0) may not be offered to others as a hosted or managed service; scanning
your own code is fine. See [rules/yara](../../rules/yara/README.md).

## Baselines and gates

```bash
python3 tools/dso/dso.py gate --input "$report_dir/report.json" \
  --baseline /private/path/approved-baseline.json --fail-on high
```

Without a baseline, all findings at or above the threshold block. With one, only
new or severity-escalated findings block. Unknown severity always blocks, with or
without a baseline. Both reports must be complete and have the same project
and target. A scan that covers less than its baseline is incomparable (exit 2,
`mismatch` names the cause): a plugin of the baseline was not run, an exclusion
was added, or the profile drops kit files or rule directories the baseline
used. Findings there could otherwise disappear unseen. Other coverage changes
(scanner versions, rules, DSO code in `policy_digest`, added plugins, removed
exclusions, the engine) stay comparable and are listed in `coverage_changes`:
a baseline only accepts exact finding IDs, so they can only add findings, and a
kit update does not force every team to re-approve its baseline. Gate output
lists `resolved` baseline IDs and `fix_changed` findings only for comparable
scans.
No baseline is implicitly generated or refreshed. Review a completed report and
store an approved copy through your team's protected process.

Finding IDs hash tool, rule, relative path, line, package, installed version and,
for secrets, a fingerprint of the matched value. They remain stable for
identical content across runs, engines and checkout roots. Moving source lines or
files creates new findings deliberately. Duplicate identities within a scanner
collapse to the highest severity (unknown wins). Findings from different tools
remain separate, but a baseline decision about a dependency is about the
vulnerability, not the scanner: the same advisory, package and version reported
by another tool (after adding Grype or OSV-Scanner to a Trivy baseline, say) is
accepted at the severity the baseline accepted, and only a higher severity, an
unknown one, another version or another lockfile blocks. Secrets never cross
tools this way, because a rotated secret on the same line must stay new.

A baseline can waive existing high/critical findings: protect it and its selected
commit from untrusted PR changes. These JSON files are not signed evidence and
contain secret fingerprints, so keep them private.

### Exceptions with an expiry

A baseline accepts everything it contains. For one decision at a time, with a
name, a reason and a deadline, use the exception register
([example](../../reporting/exceptions.example.json)):

```bash
dso triage --input report.json --exceptions /private/path/exceptions.json
dso gate --input report.json --exceptions /private/path/exceptions.json
dso exceptions --input /private/path/exceptions.json      # review the register itself
```

`dso triage` shows each blocking issue and, for the ones you accept, asks for an
owner, a different approver, a reason, a compensating control, a ticket and the
days until expiry (1-90), then appends one entry per rule of the issue to the
register, with `tool` set to `*` when several tools report that rule (one
advisory from three dependency scanners is one decision). `dso gate --exceptions`
stops the findings an active entry
matches from blocking, whatever their severity: a reviewed decision outranks a
scanner's guess, unknown severity included. An entry matches by `tool` (a plugin
name, or `*`), exact `rule_id` and `asset_id` (the report's project, or `*`),
and a dependency entry covers its whole issue, whichever tool reported it. An
expired entry waives nothing and is listed as expired while findings still match
it; an entry that matches nothing is listed as unused; one that expires within
14 days is pointed out. A register with a structural problem (missing fields,
owner equal to approver, a date out of range, duplicates) is refused as a whole
and the gate exits 2. The gate output carries this under `exceptions`.

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
# All repository adapters with reviewed Docker images (YARA is native-only).
python3 tools/dso/tests/smoke.py --engine docker --profile audit \
  --plugins gitleaks semgrep trivy trufflehog grype osv-scanner trivy-config poutine
# Both image adapters, twice against the same architecture-specific Alpine digest.
python3 tools/dso/tests/smoke_image.py --engine docker
```

Unit tests cover adapters, multi-line and rotated secrets, deduplication, cross-tool issues,
the snapshot inventory and gaps, the exception register, gate waivers and triage,
delta/escalation and unknown-severity gates, coverage changes, snapshot rules
(ignore files, symlinks, special and unreadable files), incomplete scans,
timeouts, cancellation, diagnostics, private output and existing commands. The
repository smoke test checks detections, blocking, secret redaction and clean fixes
with the same runner. The image smoke checks both adapters and repeat/baseline
stability. Neither test executes application code or the target image.
Delete private output reports when finished.
Snapshots, raw scanner reports and scanner temporary files are removed by the
runner, including after an interrupt. Keep real findings outside public git.
Original code is MIT licensed.
