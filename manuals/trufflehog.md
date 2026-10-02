# TruffleHog

**Version reviewed:** v3.97.9 ([official release](https://github.com/trufflesecurity/trufflehog/releases/tag/v3.97.9)); metadata checked 2026-10-02.

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

**Verified release package (Linux amd64)**

The checksum below was read from the official release metadata on 2026-10-02.
Use the matching release asset/checksum for another OS or architecture.
SHA256 pinning checks integrity; review upstream signatures/provenance before
trusting a new release.

```bash
set -eu
curl --fail --show-error --location https://github.com/trufflesecurity/trufflehog/releases/download/v3.97.9/trufflehog_3.97.9_linux_amd64.tar.gz -o trufflehog.tar.gz
printf '%s  %s\n' '40377e6572495412fb9ba0bc21c9401f73b72f1d2afd11b9931bc4a5ed622866' 'trufflehog.tar.gz' | sha256sum --check -
tar -xzf trufflehog.tar.gz trufflehog
sudo install -m 0755 trufflehog /usr/local/bin/trufflehog
```

On macOS, `brew install trufflehog` is a convenient alternative; verify its installed
version before using it with a pinned CI setup.

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
  image: ubuntu:24.04@sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60
  variables:
    SCAN_PATH: "."
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - |
      curl --fail --show-error --location https://github.com/trufflesecurity/trufflehog/releases/download/v3.97.9/trufflehog_3.97.9_linux_amd64.tar.gz -o trufflehog.tar.gz
      printf '%s  %s\n' '40377e6572495412fb9ba0bc21c9401f73b72f1d2afd11b9931bc4a5ed622866' 'trufflehog.tar.gz' | sha256sum --check -
      tar -xzf trufflehog.tar.gz trufflehog
      install -m 0755 trufflehog /usr/local/bin/trufflehog
  script:
    - trufflehog filesystem "$SCAN_PATH" --no-verification --fail --json > trufflehog.jsonl
  artifacts:
    when: always
    expire_in: 7 days
    paths: [trufflehog.jsonl]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

The CI example disables provider verification and preserves the scanner exit
code. Restrict report access: native JSON can include secret values. Do not pipe
the scanner into a formatter unless the shell preserves pipeline failures.

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
