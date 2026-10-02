# DSO repository scanning, MCP and installation

Reviewed 2026-10-02. Original orchestration code; no new rule packs imported.

## Decision

Extend the existing standard-library CLI with Gitleaks current-tree secrets,
Semgrep's three local Python starter rules and Trivy filesystem dependency
vulnerabilities. Keep scanner execution and gate policy separate. Normalize only
allowlisted fields; never return raw secret matches, code snippets or diagnostic
output. Secrets are identified by a domain-separated SHA-256 fingerprint so a
rotated secret at the same location is a new finding.

Scanners read a private snapshot of the target, not the target itself. QA showed
that scanners silently skip unreadable files, honour target ignore files
(including Gitleaks' unconditional `<source>/.gitleaksignore`), apply Semgrep's
built-in ignores and size limit, and follow git ownership rules that differ by
UID. The snapshot makes all of these explicit: unreadable and special files,
symlinks and control-character paths fail the scan unless a reviewed exclusion is
recorded in coverage. Trivy runs offline, because online Java resolution sent
target-supplied repository URLs and private coordinates to the network and was
rate-limited by Maven Central.

Gates use exact finding IDs. Incomplete scans always fail. Unknown severity
always blocks, even with a baseline. A baseline must match the project; other
coverage changes are reported and still compared, because accepting exact IDs
cannot hide new findings and kit updates should not break every consumer. This
does not implement external lifecycle closure, owner/SLA enrichment or automatic
risk exception application.

The MCP server in `mcp/dso` imports the shared core and uses the official Python
SDK's low-level server with a non-blocking stdio transport, so scans run in a
worker thread, the server stays responsive and cancellation, EOF and signals stop
scanner processes and containers. Reports stay server-side behind IDs, and only
the server's own scans can be gated. Version 1.29.0 of the SDK is pinned because
Semgrep 1.179.0 requires that exact version. Stdio avoids a network listener and
requires an explicit allowed directory. Docker clients need no daemon socket
inside the DSO image.

Two installation paths are provided: a private standalone virtual environment
with hash-locked Python packages and checksum-verified platform binaries, and a
multi-stage Docker build with pinned base/scanner digests, hash-locked Python
packages, a timestamp-pinned Debian snapshot and an SBOM. The image rebuilds
Gitleaks v8.30.1 from its reviewed commit with Go 1.26.6 and current
`golang.org/x/crypto`/`x/text`, because the upstream binary carries fixed Go
vulnerabilities. Binary release digests are recorded for Linux and macOS amd64/arm64.

## Acceptance

- Unit tests: adapters, multi-line and rotated secrets, sensitive-field omission,
  duplicate identities, new/escalated/unknown findings, incomplete current and
  baseline scans, coverage changes, snapshot rules, timeouts, cancellation,
  diagnostics and private atomic output.
- Installer tests: wrong SHA256 rejected, only the named regular executable
  extracted, symlink archives rejected, platform manifest checked.
- Actual MCP SDK client: initialize, list tools, reject path escapes, unknown
  arguments and gating of imported reports, read/page reports. Repeated through
  `docker run -i`, including a real scan and gate. A ping during a scan is
  answered immediately; MCP cancellation stops native processes and containers.
- Real Gitleaks 8.30.1, Semgrep 1.179.0 and Trivy 0.75.0: the synthetic vulnerable
  repository is detected and blocks with every scanner; the fixed repository
  produces zero findings. Native and host-Docker on macOS arm64 and the
  self-contained Linux arm64 image pass, and native and Docker produce identical
  finding IDs. Linux amd64 runs in CI (`dso-container` job).
- Interrupting the CLI with SIGINT, SIGTERM or SIGHUP leaves no scanner process,
  container or temporary directory.
- GitLab template emulated as a shell executor on Bash 3.2 (no baseline, new
  secret, clean merge request, unreachable baseline, invalid reference); syntax
  checked on Bash 4.2–5.2. Workflows pass actionlint and yamllint.
- The image has no fixable HIGH/CRITICAL findings in Trivy; the remaining HIGH
  findings are Debian packages without an upstream fix.
- Caller-project GitHub/GitLab execution still needs acceptance in consuming
  projects. Workflow pins and baseline references need protected review.

Source locations/line shifts intentionally produce new IDs. A completed scan means
the selected tools completed within their stated profile, not that all
languages, assets or vulnerability databases have been independently verified.

## Sources

- [MCP Python SDK v1](https://py.sdk.modelcontextprotocol.io/v1/)
- [Gitleaks 8.30.1](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)
- [Semgrep 1.179.0 package](https://pypi.org/project/semgrep/1.179.0/)
- [Trivy 0.75.0](https://github.com/aquasecurity/trivy/releases/tag/v0.75.0)

See [DSO CLI](../../tools/dso/README.md), [MCP and installation](../../mcp/dso/README.md),
and [report contract](../../reporting/dso-report.md).
