# TruffleHog

**Area:** 1. Protect your code → Secret scanning  
**License:** AGPL-3.0  
**Notes:** Ready GitLab CI example upstream

[GitHub: trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) · [Documentation](https://docs.trufflesecurity.com)

## What it is for

Finds secrets and checks with the provider whether they still work.

Verification removes most noise: `--results=verified` shows only credentials that still authenticate. It can also scan a whole GitLab instance, issues and all, with `trufflehog gitlab`.

> [!WARNING]
> Verification makes network calls to the providers of the secrets it finds. Check that this is acceptable before running it in CI.

## Install

**Homebrew**

```bash
brew install trufflehog
```

**Install script**

```bash
curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
```

**Container image**

```bash
docker pull trufflesecurity/trufflehog:latest
```

## Use

**Scan the local repository, fail on live or unknown secrets**

```bash
trufflehog git file://. --results=verified,unknown --fail
```

**Scan a directory**

```bash
trufflehog filesystem path/to/dir
```

**JSON or SARIF output**

```bash
trufflehog git file://. --json > trufflehog.jsonl
trufflehog filesystem . --sarif --no-verification > trufflehog.sarif
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
trufflehog:
  stage: test
  image: alpine:3.20
  variables:
    SCAN_PATH: "."
  before_script:
    - apk add --no-cache git curl jq
    - curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
  script:
    - trufflehog filesystem "$SCAN_PATH" --results=verified,unknown --fail --json | jq
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

## Output and triage

Exit code 183 means secrets were found (only with `--fail`), 1 means an error, 0 means clean. Verified results are live credentials: revoke them immediately.

## Concepts to know

- Secret detection
- Pre-commit hooks
- Full git history scans
- Verified vs unverified findings
- Rotate first, then remove
- Secret zero

## Related tools

- [gitleaks](gitleaks.md) — Fast regex and entropy scanner for git history, directories, and stdin.
- [betterleaks](betterleaks.md) — Successor to gitleaks by the same author; reads .gitleaks.toml and validates findings.
- [detect-secrets](detect-secrets.md) — Baseline workflow: record known findings once, then block only new secrets.
