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
pipx install zizmor
# or
docker pull ghcr.io/zizmorcore/zizmor:latest
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
      - uses: actions/checkout@v7          # pin to a commit SHA
        with:
          persist-credentials: false
      - uses: zizmorcore/zizmor-action@v0.6.4
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
