# pinact

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** MIT  
**Notes:** GitHub Actions only

[GitHub: suzuki-shunsuke/pinact](https://github.com/suzuki-shunsuke/pinact) · [Documentation](https://github.com/suzuki-shunsuke/pinact/tree/main/docs)

## What it is for

Pins GitHub Actions and reusable workflows to full commit SHAs.

A moved tag is how many Actions supply-chain attacks spread. pinact rewrites `uses:` lines to SHAs with a version comment.

## Install

**Homebrew**

```bash
brew install pinact
```

## Use

**Pin every action in the repository**

```bash
pinact run
```

**Check only, for CI**

```bash
pinact run --check
```

## Output and triage

Exit code 1 means something still needs pinning, 2 means an action cannot be fixed automatically, 3 means an API or usage error.

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
- [actionlint](actionlint.md) — Linter for GitHub Actions workflows, including shellcheck on run: steps.
- [Harden-Runner](harden-runner.md) — Monitors and blocks network egress and file changes on GitHub-hosted runners.
- [Checkov (gitlab_ci)](checkov-cicd.md) — Policy checks for .gitlab-ci.yml and GitLab project settings.
- [OpenSSF Scorecard](scorecard.md) — Scores a repository on security practices: reviews, pinning, branch protection.
