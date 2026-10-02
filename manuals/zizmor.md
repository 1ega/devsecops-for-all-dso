# zizmor

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** MIT  
**Notes:** GitHub Actions only; SARIF output

[GitHub: zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) · [Documentation](https://docs.zizmor.sh/)

## What it is for

Static analysis for GitHub Actions: template injection, unpinned actions, excessive permissions.

The most thorough auditor for GitHub workflows. It finds the injection and token-permission mistakes behind most real Actions compromises.

## Install

**Homebrew, pipx, or container**

```bash
brew install zizmor
# or
pipx install zizmor==1.30.1
# or
docker pull ghcr.io/zizmorcore/zizmor:1.30.1@sha256:a2eb396d886c053073405c7a980f2139ba2248ec172243cfa3841e57196e8101
```

## Use

**Audit the workflows in a repository**

```bash
zizmor .
```

**SARIF output**

```bash
zizmor --format=sarif . > zizmor.sarif
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitHub Actions

```yaml
name: zizmor
on:
  push:
    branches: [main]
  pull_request:
permissions: {}
jobs:
  zizmor:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      actions: read
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
        with:
          persist-credentials: false
      - uses: zizmorcore/zizmor-action@cc914d7f3750a2d13d75c7f184a1060aa0e9d482
```

## Output and triage

Exit codes 11 to 14 give the highest finding severity (informational to high); with `--format=sarif` it exits 0 and the results live in the SARIF file.

## Concepts to know

- Hosted vs self-hosted runners
- Protected and masked variables
- Pipeline templates and includes
- Pipeline triggers
- Poisoned pipeline execution
- OIDC id_tokens
- Unpinned images and includes

## Related tools

- [poutine](poutine.md) — Finds injection, unpinned includes, and risky runners in .gitlab-ci.yml and other pipelines.
- [actionlint](actionlint.md) — Linter for GitHub Actions workflows, including shellcheck on run: steps.
- [pinact](pinact.md) — Pins GitHub Actions and reusable workflows to full commit SHAs.
- [Harden-Runner](harden-runner.md) — Monitors and blocks network egress and file changes on GitHub-hosted runners.
- [Checkov (gitlab_ci)](checkov-cicd.md) — Policy checks for .gitlab-ci.yml and GitLab project settings.
- [OpenSSF Scorecard](scorecard.md) — Scores a repository on security practices: reviews, pinning, branch protection.

## Adoption, tuning and verification

Record the tool version, rule/database revision, target scope and owner with every report.
Use the [starter integrations](../integrations/README.md) where applicable; test
expected findings and scanner failures before requiring a gate. Suppress only
reviewed false positives with asset/rule scope, approver and expiry. Retest the
deployed version, retain redacted evidence privately, and follow the
[finding lifecycle](../reporting/finding-lifecycle.md). Missing packages, denied
APIs, incomplete checkout or skipped targets are coverage gaps, not a clean scan.
