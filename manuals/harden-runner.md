# Harden-Runner

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** Apache-2.0  
**Notes:** GitHub Actions only

[GitHub: step-security/harden-runner](https://github.com/step-security/harden-runner) · [Documentation](https://docs.stepsecurity.io/harden-runner)

## What it is for

Monitors and blocks network egress and file changes on GitHub-hosted runners.

If a dependency or action is compromised, egress control stops it from sending your secrets out. Start in audit mode to learn what each job contacts.

> [!WARNING]
> The free Community tier covers public repositories on GitHub-hosted runners; private repositories and self-hosted runners need the Enterprise tier.

## Use

**Add as the first step of every job**

```yaml
steps:
  - name: Harden Runner
    uses: step-security/harden-runner@v2.21.1   # pin to a commit SHA
    with:
      egress-policy: audit
```

## Output and triage

Each run links to a report of network and file events. Switch `egress-policy` to `block` with an allowlist once the audit is clean.

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
- [Checkov (gitlab_ci)](checkov-cicd.md) — Policy checks for .gitlab-ci.yml and GitLab project settings.
- [OpenSSF Scorecard](scorecard.md) — Scores a repository on security practices: reviews, pinning, branch protection.
