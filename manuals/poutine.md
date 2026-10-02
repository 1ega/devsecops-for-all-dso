# poutine

**Area:** 2. Secure the pipeline → Pipeline security  
**License:** Apache-2.0  
**Notes:** Understands GitLab CI; scans groups via the API  
**Recommended first choice in this topic.**

[GitHub: boostsecurityio/poutine](https://github.com/boostsecurityio/poutine) · [Documentation](https://boostsecurityio.github.io/poutine/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/cicd/poutine-rego)

## What it is for

Finds injection, unpinned includes, and risky runners in .gitlab-ci.yml and other pipelines.

One of the few pipeline scanners that understands GitLab CI as well as GitHub Actions. Its Rego rules are imported in this repository, so you can read exactly what each check looks for.

## Install

**Homebrew**

```bash
brew install poutine
```

**Go**

```bash
go install github.com/boostsecurityio/poutine@latest
```

## Use

**Scan the pipeline files in the current repository**

```bash
poutine analyze_local .
```

**Scan a whole GitLab group**

```bash
poutine analyze_org my-group --scm gitlab \
  --scm-base-url https://gitlab.example.com --token "$GL_TOKEN"
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
poutine:
  stage: test
  image: golang:1.27
  before_script:
    - go install github.com/boostsecurityio/poutine@latest
  script:
    - poutine analyze_local . --format sarif > poutine.sarif
    - poutine analyze_local . --fail-on-violation
  artifacts:
    when: always
    paths: [poutine.sarif]
```

## Output and triage

`--fail-on-violation` exits 10 when violations are found. For GitLab API scans pass the token with `--token`; the CLI only reads `GH_TOKEN` from the environment. Disable the daily version check with `--disable-version-check`.

## Concepts to know

- Hosted vs self-hosted runners
- Protected and masked variables
- Pipeline templates and includes
- Pipeline triggers
- Poisoned pipeline execution
- OIDC id_tokens
- Unpinned images and includes

## Related tools

- [zizmor](zizmor.md) — Static analysis for GitHub Actions: template injection, unpinned actions, excessive permissions.
- [actionlint](actionlint.md) — Linter for GitHub Actions workflows, including shellcheck on run: steps.
- [pinact](pinact.md) — Pins GitHub Actions and reusable workflows to full commit SHAs.
- [Harden-Runner](harden-runner.md) — Monitors and blocks network egress and file changes on GitHub-hosted runners.
- [Checkov (gitlab_ci)](checkov-cicd.md) — Policy checks for .gitlab-ci.yml and GitLab project settings.
- [OpenSSF Scorecard](scorecard.md) — Scores a repository on security practices: reviews, pinning, branch protection.
