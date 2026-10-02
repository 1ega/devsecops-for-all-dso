# mobsfscan

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** LGPL-3.0  
**Notes:** Writes GitLab SAST reports

[GitHub: MobSF/mobsfscan](https://github.com/MobSF/mobsfscan) · [Documentation](https://github.com/MobSF/mobsfscan#readme) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/rules/semgrep/mobile)

## What it is for

Source code checks for Android and iOS apps with native GitLab SAST output.

The quickest way to add mobile-specific checks to a GitLab pipeline. Combine it with the mobile Semgrep pack in this repository for deeper coverage.

## Install

**pip or container image**

```bash
pip install mobsfscan
# or
docker pull opensecurity/mobsfscan
```

## Use

**Scan with SARIF output**

```bash
mobsfscan . --sarif --output mobsfscan.sarif
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
mobsfscan:
  stage: test
  image: python:3.12
  before_script:
    - pip3 install --upgrade mobsfscan
  script:
    - mobsfscan . --gitlab-sast -o gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
```

## Output and triage

Exit code 1 on ERROR-severity findings; `--exit-warning` also fails on warnings and `--no-fail` always returns 0.

## Concepts to know

- Taint analysis
- Injection: SQL, command, template
- SSRF
- Weak cryptography
- False positives and triage
- Diff-aware scans

## Related tools

- [Semgrep](semgrep.md) — Pattern and taint rules for 30+ languages, with native GitLab SAST output.
- [Opengrep](opengrep.md) — Community fork of the Semgrep engine with the same rule format and CLI.
- [gosec](gosec.md) — Security checks for Go code: injection, weak crypto, unsafe file and network use.
- [Find Security Bugs](find-sec-bugs.md) — SpotBugs plugin with security detectors for Java, Kotlin, and JVM frameworks.
- [eslint-plugin-security](eslint-security.md) — ESLint rules for risky JavaScript and TypeScript patterns.
- [SonarQube](sonarqube.md) — Code quality and security server with quality gates and per-branch dashboards.
