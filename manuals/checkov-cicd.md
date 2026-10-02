# Checkov (gitlab_ci)

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** Apache-2.0  
**Notes:** gitlab_ci and gitlab_configuration frameworks; GitLab SAST output

[GitHub: bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) · [Documentation](https://www.checkov.io/1.Welcome/Quick%20Start.html)

## What it is for

Policy checks for .gitlab-ci.yml and GitLab project settings.

If you already run Checkov for Terraform, the same tool checks pipeline files and GitLab configuration with no extra setup.

## Install

**pip or Homebrew**

```bash
pip3 install checkov
# or
brew install checkov
```

## Use

**Check pipeline definitions**

```bash
checkov -d . --framework gitlab_ci
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
checkov-pipeline:
  stage: test
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d . --framework gitlab_ci -o cli -o gitlab_sast --output-file-path console,gl-sast-checkov.json
  artifacts:
    reports:
      sast: gl-sast-checkov.json
```

## Output and triage

Exits non-zero on failed checks; `--soft-fail` always returns 0, and `--hard-fail-on` limits failures to chosen check IDs or severities.

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
- [OpenSSF Scorecard](scorecard.md) — Scores a repository on security practices: reviews, pinning, branch protection.
