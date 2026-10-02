# Opengrep

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** LGPL-2.1  
**Notes:** Writes GitLab SAST reports

[GitHub: opengrep/opengrep](https://github.com/opengrep/opengrep) · [Documentation](https://github.com/opengrep/opengrep/wiki)

## What it is for

Community fork of the Semgrep engine with the same rule format and CLI.

Choose it if you want an engine whose features are all open source. Existing Semgrep rules, including the packs in this repository, run unchanged.

## Install

**Install script (Linux and macOS)**

```bash
curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
```

## Use

**Scan with SARIF output**

```bash
opengrep scan --sarif-output=opengrep.sarif -f rules/ path/to/code
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
opengrep:
  stage: test
  image: debian:bookworm-slim
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
    - export PATH="$HOME/.opengrep/cli/latest:$PATH"
  script:
    - opengrep scan -f rules/ --gitlab-sast-output=gl-sast-report.json .
  artifacts:
    reports:
      sast: gl-sast-report.json
```

## Output and triage

`--error` exits 1 on findings. No official container image is published; install with the script.

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
