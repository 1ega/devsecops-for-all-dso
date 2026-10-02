# actionlint

**Version reviewed:** v1.7.12 ([official release](https://github.com/rhysd/actionlint/releases/tag/v1.7.12)); metadata checked 2026-10-02.

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
go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.12
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
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - name: Download verified actionlint
        run: |
          curl --fail --show-error --location https://github.com/rhysd/actionlint/releases/download/v1.7.12/actionlint_1.7.12_linux_amd64.tar.gz -o actionlint.tar.gz
          printf '%s  %s\n' '8aca8db96f1b94770f1b0d72b6dddcb1ebb8123cb3712530b08cc387b349a3d8' 'actionlint.tar.gz' | sha256sum --check -
          tar -xzf actionlint.tar.gz actionlint
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
