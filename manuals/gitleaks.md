# gitleaks

**Area:** 1. Protect your code → Secret scanning  
**License:** MIT  
**Notes:** SARIF and JSON reports  
**Recommended first choice in this topic.**

[GitHub: gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) · [Documentation](https://github.com/gitleaks/gitleaks#readme) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/scanners/gitleaks)

## What it is for

Fast regex and entropy scanner for git history, directories, and stdin.

The most widely used open-source secret scanner, with a simple TOML config you can extend with your own rules (`[extend] useDefault = true`). Start with it in pre-commit and in pull request pipelines.

> [!WARNING]
> The README says gitleaks is feature complete and will receive security patches only; its author now develops betterleaks. It remains a solid choice today.

## Install

**macOS or Linux (Homebrew)**

```bash
brew install gitleaks
```

**Container image**

```bash
docker pull zricethezav/gitleaks:latest
# or ghcr.io/gitleaks/gitleaks:latest
```

## Use

**Scan the git history of the current repository**

```bash
gitleaks git -v .
```

**Scan a directory without git history**

```bash
gitleaks dir -v path/to/project
```

**Write a SARIF report**

```bash
gitleaks git --report-format sarif --report-path gitleaks.sarif .
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
secret-scan:
  stage: test
  image:
    name: zricethezav/gitleaks:latest   # pin a version tag
    entrypoint: [""]
  variables:
    GIT_DEPTH: 0                        # full history for the scan
  script:
    - gitleaks git --report-format sarif --report-path gitleaks.sarif .
  artifacts:
    when: always
    paths: [gitleaks.sarif]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Output and triage

Exit code 0 means no leaks; 1 means leaks were found (change it with `--exit-code`). Treat every finding as compromised: rotate the secret first, then remove it from history. Add justified false positives to `.gitleaksignore`. Import the SARIF file into DefectDojo as "Gitleaks Scan" or "SARIF".

## Concepts to know

- Secret detection
- Pre-commit hooks
- Full git history scans
- Verified vs unverified findings
- Rotate first, then remove
- Secret zero

## Related tools

- [TruffleHog](trufflehog.md) — Finds secrets and checks with the provider whether they still work.
- [betterleaks](betterleaks.md) — Successor to gitleaks by the same author; reads .gitleaks.toml and validates findings.
- [detect-secrets](detect-secrets.md) — Baseline workflow: record known findings once, then block only new secrets.
