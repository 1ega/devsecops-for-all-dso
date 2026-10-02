# actionlint

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** MIT  
**Notes:** GitHub Actions only

[GitHub: rhysd/actionlint](https://github.com/rhysd/actionlint) · [Documentation](https://github.com/rhysd/actionlint/tree/main/docs)

## What it is for

Linter for GitHub Actions workflows, including shellcheck on run: steps.

Catches broken expressions, wrong types, and unsafe shell before a workflow ever runs. Cheap to add next to zizmor.

## Install

**Homebrew or Go**

```bash
brew install actionlint
# or
go install github.com/rhysd/actionlint/cmd/actionlint@latest
```

## Use

**Lint all workflows in the repository**

```bash
actionlint
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitHub Actions

```yaml
name: actionlint
on: [pull_request]
permissions:
  contents: read
jobs:
  actionlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
      - name: Download actionlint
        run: bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
      - name: Lint workflows
        run: ./actionlint -color
```

## Output and triage

Exits non-zero when it finds errors. Output can be shaped with `-format`, including SARIF through a template.

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
- [zizmor](zizmor.md) — Static analysis for GitHub Actions: template injection, unpinned actions, excessive permissions.
- [pinact](pinact.md) — Pins GitHub Actions and reusable workflows to full commit SHAs.
- [Harden-Runner](harden-runner.md) — Monitors and blocks network egress and file changes on GitHub-hosted runners.
- [Checkov (gitlab_ci)](checkov-cicd.md) — Policy checks for .gitlab-ci.yml and GitLab project settings.
- [OpenSSF Scorecard](scorecard.md) — Scores a repository on security practices: reviews, pinning, branch protection.
