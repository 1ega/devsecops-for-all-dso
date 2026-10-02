# betterleaks

**Area:** 1. Protect your code → Secret scanning  
**License:** MIT  
**Notes:** JSON reports; can scan GitLab issues, MRs, and CI logs

[GitHub: betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) · [Documentation](https://github.com/betterleaks/betterleaks#readme)

## What it is for

Successor to gitleaks by the same author; reads .gitleaks.toml and validates findings.

Worth watching if you already use gitleaks: it keeps the config format, adds rule validation, and can scan GitLab projects directly, including merge requests and CI job logs.

> [!WARNING]
> Version 2 removed SARIF output: reports are JSON or JSONL only. Several flags were renamed from gitleaks, for example `--report-path` became `--output`.

## Install

**Homebrew**

```bash
brew install betterleaks
```

**Go**

```bash
go install github.com/betterleaks/betterleaks/v2@latest
```

**Container image**

```bash
docker pull ghcr.io/betterleaks/betterleaks:v2
```

## Use

**Scan the git history**

```bash
betterleaks git .
```

**Scan a directory to JSON**

```bash
betterleaks fs . --output findings.json
```

**Scan a GitLab project (reads GITLAB_TOKEN)**

```bash
betterleaks gitlab https://gitlab.com/mygroup/myproject --include issues,mrs,releases,ci-jobs
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
betterleaks:
  stage: test
  image:
    name: ghcr.io/betterleaks/betterleaks:v2
    entrypoint: [""]
  variables:
    GIT_DEPTH: 0
  script:
    - betterleaks git . --output betterleaks.json
  artifacts:
    when: always
    paths: [betterleaks.json]
```

## Output and triage

Exit code 1 when findings exist (change with `--exit-code`).

## Concepts to know

- Secret detection
- Pre-commit hooks
- Full git history scans
- Verified vs unverified findings
- Rotate first, then remove
- Secret zero

## Related tools

- [gitleaks](gitleaks.md) — Fast regex and entropy scanner for git history, directories, and stdin.
- [TruffleHog](trufflehog.md) — Finds secrets and checks with the provider whether they still work.
- [detect-secrets](detect-secrets.md) — Baseline workflow: record known findings once, then block only new secrets.
