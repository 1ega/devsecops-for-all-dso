# Opengrep

**Version reviewed:** v1.30.0 ([official release](https://github.com/opengrep/opengrep/releases/tag/v1.30.0)); metadata checked 2026-10-02.

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** LGPL-2.1  
**Notes:** Writes GitLab SAST reports

[GitHub: opengrep/opengrep](https://github.com/opengrep/opengrep) · [Documentation](https://github.com/opengrep/opengrep/wiki)

## What it is for

Community fork of the Semgrep engine with the same rule format and CLI.

Choose it if you want an engine whose features are all open source. Its rule syntax overlaps with Semgrep. Test every chosen pack with the pinned
engine; compatibility and feature coverage vary.

## Install

**Verified release package (Linux amd64)**

The checksum below was read from the official release metadata on 2026-10-02.
Use the matching release asset/checksum for another OS or architecture.
SHA256 pinning checks integrity; review upstream signatures/provenance before
trusting a new release.

```bash
set -eu
curl --fail --show-error --location https://github.com/opengrep/opengrep/releases/download/v1.30.0/opengrep_manylinux_x86 -o opengrep
printf '%s  %s\n' '35779bdd72e92129c8df2a77f0c55e8c08356801ea92591ef32108d6b28d564c' 'opengrep' | sha256sum --check -
sudo install -m 0755 opengrep /usr/local/bin/opengrep
```

## Use

**Scan with SARIF output**

```bash
opengrep scan --sarif-output=opengrep.sarif -f rules/semgrep/python/ path/to/code
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
opengrep:
  stage: test
  image: ubuntu:24.04@sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - |
      curl --fail --show-error --location https://github.com/opengrep/opengrep/releases/download/v1.30.0/opengrep_manylinux_x86 -o opengrep
      printf '%s  %s\n' '35779bdd72e92129c8df2a77f0c55e8c08356801ea92591ef32108d6b28d564c' 'opengrep' | sha256sum --check -
      install -m 0755 opengrep /usr/local/bin/opengrep
  script:
    - opengrep scan -f rules/semgrep/python/ --gitlab-sast-output=gl-sast-report.json .
  artifacts:
    reports:
      sast: gl-sast-report.json
```

## Output and triage

`--error` exits 1 on findings. The example installs a verified release binary. Test engine/rule compatibility
and distinguish findings from scanner execution errors before enabling a gate.

## Concepts to know

- Taint analysis
- Injection: SQL, command, template
- SSRF
- Weak cryptography
- False positives and triage
- Diff-aware scans

## Related tools

- [Semgrep](semgrep.md) — Pattern and taint rules for 30+ languages, with native GitLab SAST output.
- [gosec](gosec.md) — Security checks for Go code: injection, weak crypto, unsafe file and network use.
- [Find Security Bugs](find-sec-bugs.md) — SpotBugs plugin with security detectors for Java, Kotlin, and JVM frameworks.
- [eslint-plugin-security](eslint-security.md) — ESLint rules for risky JavaScript and TypeScript patterns.
- [mobsfscan](mobsfscan.md) — Source code checks for Android and iOS apps with native GitLab SAST output.
- [SonarQube](sonarqube.md) — Code quality and security server with quality gates and per-branch dashboards.
