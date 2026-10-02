# detect-secrets

**Area:** 1. Protect your code → Secret scanning  
**License:** Apache-2.0

[GitHub: Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) · [Documentation](https://github.com/Yelp/detect-secrets#readme)

## What it is for

Baseline workflow: record known findings once, then block only new secrets.

Fits large legacy repositories where a first scan finds hundreds of old findings. You audit the baseline once and the hook only fails on secrets that are not in it.

## Install

**pip or Homebrew**

```bash
pip install detect-secrets
# or
brew install detect-secrets
```

## Use

**Create and review a baseline**

```bash
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
```

**Fail on secrets that are not in the baseline**

```bash
git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
detect-secrets:
  stage: test
  image: python:3.12-slim
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends git
    - pip install detect-secrets
  script:
    - git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline
```

## Output and triage

The hook exits 1 when it finds secrets missing from the baseline and 3 when it updated the baseline file. Commit the reviewed baseline to the repository.

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
- [betterleaks](betterleaks.md) — Successor to gitleaks by the same author; reads .gitleaks.toml and validates findings.
