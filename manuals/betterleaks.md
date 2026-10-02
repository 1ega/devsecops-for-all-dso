# betterleaks

**Version reviewed:** v1.9.0 ([official release](https://github.com/betterleaks/betterleaks/releases/tag/v1.9.0)); metadata checked 2026-10-02.

**Area:** 1. Protect your code → Secret scanning  
**License:** MIT  
**Notes:** JSON reports; can scan GitLab issues, MRs, and CI logs

[GitHub: betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) · [Documentation](https://github.com/betterleaks/betterleaks#readme)

## What it is for

Successor to gitleaks by the same author; reads .gitleaks.toml and validates findings.

Worth watching if you already use gitleaks: it keeps the config format, adds rule validation, and can scan GitLab projects directly, including merge requests and CI job logs.

> [!WARNING]
> This manual covers the stable v1.9.0. Version 2 is still a release candidate (v2.0.0-rc.1) with no published image: it removes SARIF output and renames flags, for example `--report-path` becomes `--output`, and `dir` becomes `fs`.

## Install

**Homebrew**

```bash
brew install betterleaks
```

**Go**

```bash
go install github.com/betterleaks/betterleaks@v1.9.0
```

**Container image**

```bash
docker pull ghcr.io/betterleaks/betterleaks:v1.9.0@sha256:e3b95b0db6c2735db17165c009b0ad6d9cef34fb4578659232b98f69d7346cac
```

## Use

**Scan the git history**

```bash
betterleaks git . --redact
```

**Scan a directory to JSON**

```bash
betterleaks dir . --redact --report-format json --report-path findings.json
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
    name: ghcr.io/betterleaks/betterleaks:v1.9.0@sha256:e3b95b0db6c2735db17165c009b0ad6d9cef34fb4578659232b98f69d7346cac
    entrypoint: [""]
  variables:
    GIT_DEPTH: 0
  script:
    - betterleaks git . --redact --report-format json --report-path betterleaks.json
  artifacts:
    when: always
    paths: [betterleaks.json]
```

## Output and triage

Exit code 1 when findings exist (change with `--exit-code`). Logs and reports contain the raw secret unless you pass `--redact`. Use `--report-format sarif` for code scanning.

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
