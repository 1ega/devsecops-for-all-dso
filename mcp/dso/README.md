# DSO MCP server

A local stdio MCP server in `mcp/dso`, backed by the same scanning and gate
implementation as the [DSO CLI](../../tools/dso/README.md). Python 3.10–3.14 on
Linux or macOS is required. Default engine: Docker with the repository's pinned
images. The CLI remains dependency-free; only the MCP server needs the official SDK.

## Standalone installation

From the repository root:

```bash
bash mcp/dso/install.sh
mcp/dso/.venv/bin/python mcp/dso/server.py \
  --root /absolute/path/to/project --engine native
```

The installer installs the hash-locked MCP/Semgrep packages
(`requirements-standalone.lock`) plus SHA256-verified Gitleaks/Trivy binaries for
Linux or macOS, amd64/arm64. It installs into `mcp/dso/.venv` by default; pass
another directory as its first argument and set `PYTHON=python3.12` to choose the
interpreter. No sudo or global package changes. Both CLI and server find scanner
binaries next to their Python interpreter, so activation is optional:

```bash
mcp/dso/.venv/bin/python tools/dso/dso.py doctor
mcp/dso/.venv/bin/python tools/dso/dso.py scan repo /absolute/path/to/project \
  --project team/application --output "$(mktemp -d)/dso-report.json"
```

For an MCP-only install using external Docker instead, create a venv, run
`pip install --require-hashes -r mcp/dso/requirements.lock`, then use `--engine docker`.

The process waits for MCP messages on stdin; this is not an interactive terminal
or HTTP server. Options: `--root` (required: an existing directory other than
`/`), `--engine native|docker`, `--timeout 300` per scanner including image
pulls, and repeatable `--exclude path` for reviewed target-relative exclusions
applied to every scan. The server exits when stdin closes or on
SIGINT/SIGTERM/SIGHUP, and stops any running scanner first. Delete the virtual
environment to uninstall.

Example client configuration (replace all absolute paths):

```json
{
  "mcpServers": {
    "dso": {
      "command": "/absolute/path/to/devsecops-for-all-dso/mcp/dso/.venv/bin/python",
      "args": [
        "/absolute/path/to/devsecops-for-all-dso/mcp/dso/server.py",
        "--root", "/absolute/path/to/project",
        "--engine", "native"
      ]
    }
  }
}
```

Client-specific registration is separate; this change does not modify any user's
MCP client configuration. Set the root to the smallest directory that contains
both the target and any saved reports you intend to read.

## Self-contained Docker installation

Build from the repository root:

```bash
docker build -f mcp/dso/Dockerfile -t dso-mcp:local .
docker run --rm -i --init --read-only --cap-drop ALL \
  --security-opt no-new-privileges --memory 3g --pids-limit 256 \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,nosuid,nodev,size=2g \
  --mount type=bind,src=/absolute/path/to/project,dst=/workspace,readonly \
  --mount type=volume,src=dso-cache,dst=/cache \
  dso-mcp:local
```

The image includes Python, MCP, Gitleaks, Semgrep and Trivy and an SBOM at
`/opt/dso/sbom.cdx.json`. Scanners execute inside this container using the
`native` engine; **no Docker socket mount or privileged container is needed**.
Python packages are hash-locked, Debian packages are upgraded from a
timestamp-pinned snapshot, setuid bits are removed and pip is not shipped.
Gitleaks is rebuilt from the reviewed v8.30.1 tag with a patched Go toolchain;
the remaining scanner findings are Debian packages without a fix.

The default image user is UID 10001. Pass `--user` with an identity that can
read every source file: unreadable files make the scan incomplete. `/tmp` holds
the private snapshot, so size it for the project. The `/cache` volume keeps the
Trivy database between runs; use one UID per cache volume. Without it each
container downloads the database again. Network access is needed for that download.

Docker MCP client configuration:

```json
{
  "mcpServers": {
    "dso": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--init", "--read-only",
        "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
        "--memory", "3g", "--pids-limit", "256", "--user", "1000:1000",
        "--tmpfs", "/tmp:rw,nosuid,nodev,size=2g",
        "--mount", "type=bind,src=/absolute/path/to/project,dst=/workspace,readonly",
        "--mount", "type=volume,src=dso-cache,dst=/cache",
        "dso-mcp:local"
      ]
    }
  }
}
```

Replace `1000:1000` with the owner of the project files. Use `-i`, not `-t`: a
TTY interferes with MCP stdio framing. No ports are exposed. Compose is also
provided; [compose.sh](compose.sh) requires an absolute, existing `DSO_ROOT`:

```bash
DSO_ROOT=/absolute/path/to/project bash mcp/dso/compose.sh build
DSO_ROOT=/absolute/path/to/project DSO_UID="$(id -u)" DSO_GID="$(id -g)" \
  bash mcp/dso/compose.sh run --rm -T dso
```

The same image can run the CLI. Use a private report directory:

```bash
report_dir="$(mktemp -d)"
docker run --rm --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" --tmpfs /tmp:rw,nosuid,nodev,size=2g \
  --mount type=bind,src=/absolute/path/to/project,dst=/workspace,readonly \
  --mount type=bind,src="$report_dir",dst=/reports \
  --mount type=volume,src=dso-cache,dst=/cache \
  --entrypoint python dso-mcp:local /opt/dso/tools/dso/dso.py \
  scan repo /workspace --engine native --project team/application --output /reports/report.json

docker run --rm --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user "$(id -u):$(id -g)" \
  --mount type=bind,src="$report_dir",dst=/reports,readonly \
  --entrypoint python dso-mcp:local /opt/dso/tools/dso/dso.py \
  gate --input /reports/report.json --fail-on high
```

Reports record `native` for this bundled image and `docker` for the host CLI's
separate scanner containers. Both scan the same snapshot with the same policy,
so their finding IDs match; the gate reports the engine difference in
`coverage_changes`. Remove the local `dso-mcp:local` image and the `dso-cache`
volume to uninstall the container option. Nothing is pushed to a registry.

## Tools

| Tool | Inputs | Result |
| --- | --- | --- |
| `dso_doctor` | None | Native versions and paths, or Docker daemon version and local pinned-image availability |
| `dso_scan_repo` | `path`, `project`, optional `tools` | `report_id`, `complete`, `runs`, `coverage`, `input` and the first 50 findings |
| `dso_read_report` | `path` | Imports a saved v2 report (at most 20 MiB) as `report_id` for inspection or as a baseline |
| `dso_get_findings` | `report_id`, optional `offset`, `limit` (1–100) | One page of findings |
| `dso_gate` | `report_id` from `dso_scan_repo`, optional `baseline_id`, `fail_on` (default `high`), `offset`, `limit` | `exit_code`: 0 pass, 1 blocking, 2 incomplete or incomparable; paged `blocking`, `resolved` and `fix_changed` with totals |

Typical interaction: scan the allowed project; inspect `complete` and `runs`;
gate the returned `report_id`; optionally import a trusted baseline with
`dso_read_report` and pass its `baseline_id`. Only reports produced by
`dso_scan_repo` in the same server session can be gated, so an agent cannot gate
a fabricated report. The server keeps at most eight reports (40 MiB) in memory
and evicts the oldest; an unknown ID requires a new scan or import. One scan runs
at a time. MCP cancellation, a closed client and signals stop the scanner process
or container. Schemas reject unknown arguments. Errors use MCP `isError` with a
generic message that never echoes paths or report content. Findings themselves
are successful tool results with a gate decision. No report file is written by
`dso_scan_repo`.

## Scope and boundaries

- Explicit root required. Absolute paths and `..` outside the root are rejected
  lexically before the filesystem is touched; symlinks resolving outside the root
  are rejected. Inside a scanned tree every symlink makes the scan incomplete
  unless excluded.
- Fixed scanner commands, reviewed rules and versions; no arbitrary executable,
  shell fragment, rule URL, cloud credential, deployment or apply operation.
- Scans read a private snapshot: unreadable files, special files and target
  ignore files cannot silently shrink coverage (see the CLI README).
- Docker mounts the snapshot read-only, uses the caller's UID, drops Linux
  capabilities, limits memory/processes, disables network for Gitleaks/Semgrep
  and removes its container after use. Registry/database network access is
  needed for Trivy and image pulls. The Docker daemon retains image layers.
- Native scanners run with the server user's permissions. Path checks are an
  application boundary, not an OS sandbox; do not scan hostile trees using a
  privileged server account.
- Normalized findings omit raw secrets, matched lines and free-form scanner
  messages; secrets are represented by a fingerprint. Paths and package
  identifiers can still be sensitive. Every tool description and result marks
  returned fields as untrusted data, never agent instructions.
- The profile covers current-tree secrets, three Python SAST starter rules and
  offline Trivy dependency vulnerabilities. Cloud/Kubernetes scans, automatic
  suppression, remediation, and DefectDojo writes are not tools in this release.

## Validation

```bash
mcp/dso/.venv/bin/python -m unittest discover -s mcp/dso/tests -v
DSO_TEST_IMAGE=dso-mcp:local mcp/dso/.venv/bin/python -m unittest discover -s mcp/dso/tests -v
python3 -m unittest discover -s tools/dso/tests -v
```

Tests start the real stdio server (or the image with `DSO_TEST_IMAGE`), initialize
an SDK client, discover tools, reject path escapes, unknown arguments, missing
IDs and gating of imported reports, read and page a saved report, and, in the
image, scan and gate a real target. Scanner adapter and failure tests live with
the CLI. Real scanner acceptance is an opt-in [smoke test](../../tools/dso/tests/smoke.py).

SDK: [official Python SDK v1 documentation](https://py.sdk.modelcontextprotocol.io/v1/).
The server uses the SDK's low-level `Server` API with its own non-blocking stdio
transport and pins `mcp==1.29.0`, which Semgrep 1.179.0 also requires. Upgrading
to SDK v2 requires an explicit API migration and protocol tests. Original code
uses the repository MIT license.

Validation evidence and remaining platform/CI limits: [implementation note](../../docs/research/dso-cli-mcp.md).
