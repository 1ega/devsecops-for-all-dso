# Semgrep

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** LGPL-2.1  
**Notes:** Writes GitLab SAST reports  
**Recommended first choice in this topic.**

[GitHub: semgrep/semgrep](https://github.com/semgrep/semgrep) · [Documentation](https://semgrep.dev/docs) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/semgrep-rules)

## What it is for

Pattern and taint rules for 30+ languages, with native GitLab SAST output.

Rules look like the code they match, so the team can write its own. This repository ships rule packs for mobile, Python, and backend languages; GitLab reads the `--gitlab-sast-output` file natively.

## Install

**pip or Homebrew**

```bash
python3 -m pip install semgrep
# or
brew install semgrep
```

**Container image**

```bash
docker pull semgrep/semgrep
```

## Use

**Scan with a local rule pack**

```bash
semgrep scan --metrics=off --config semgrep-rules/trailofbits/ path/to/project
```

**Write SARIF, JSON, and GitLab reports in one run**

```bash
semgrep scan --metrics=off --config rules/ \
  --sarif-output=semgrep.sarif --json-output=semgrep.json \
  --gitlab-sast-output=gl-sast-report.json .
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
semgrep:
  stage: test
  image: semgrep/semgrep            # no entrypoint override needed
  variables:
    SEMGREP_RULES: rules/           # path to your rule pack
  script:
    - semgrep scan --metrics=off --config "$SEMGREP_RULES"
        --gitlab-sast-output=gl-sast-report.json
        --sarif-output=semgrep.sarif .
  artifacts:
    when: always
    paths: [semgrep.sarif]
    reports:
      sast: gl-sast-report.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Output and triage

Add `--error` to exit 1 when there are findings, which fails the job. Registry configs such as `p/ci` send pseudonymous metrics; local rule paths with `--metrics=off` do not. Import JSON into DefectDojo as "Semgrep JSON Report".

## Concepts to know

- Taint analysis
- Injection: SQL, command, template
- SSRF
- Weak cryptography
- False positives and triage
- Diff-aware scans

## Related tools

- [Opengrep](opengrep.md) — Community fork of the Semgrep engine with the same rule format and CLI.
- [gosec](gosec.md) — Security checks for Go code: injection, weak crypto, unsafe file and network use.
- [Find Security Bugs](find-sec-bugs.md) — SpotBugs plugin with security detectors for Java, Kotlin, and JVM frameworks.
- [eslint-plugin-security](eslint-security.md) — ESLint rules for risky JavaScript and TypeScript patterns.
- [mobsfscan](mobsfscan.md) — Source code checks for Android and iOS apps with native GitLab SAST output.
- [SonarQube](sonarqube.md) — Code quality and security server with quality gates and per-branch dashboards.
