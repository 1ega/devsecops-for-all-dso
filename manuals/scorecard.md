# OpenSSF Scorecard

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** Apache-2.0  
**Notes:** GitLab support, some checks still in validation

[GitHub: ossf/scorecard](https://github.com/ossf/scorecard) · [Documentation](https://scorecard.dev)

## What it is for

Scores a repository on security practices: reviews, pinning, branch protection.

A quick health check of your own projects and of the open-source projects you depend on.

> [!WARNING]
> On GitLab the Dangerous-Workflow, SAST, and Token-Permissions checks are unsupported, and several others are still being validated.

## Install

**Homebrew**

```bash
brew install scorecard
```

## Use

**Score a GitLab project (token scopes: read_api, read_user, read_repository)**

```bash
export GITLAB_AUTH_TOKEN=glpat-xxxx
scorecard --repo gitlab.com/<group>/<project> --show-details
```

## Output and triage

Each check scores 0 to 10 with a reason. Use `--format=json` for automation; SARIF exists in the code but needs `ENABLE_SARIF` set.

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
- [pinact](pinact.md) — Pins GitHub Actions and reusable workflows to full commit SHAs.
- [Harden-Runner](harden-runner.md) — Monitors and blocks network egress and file changes on GitHub-hosted runners.
- [Checkov (gitlab_ci)](checkov-cicd.md) — Policy checks for .gitlab-ci.yml and GitLab project settings.
