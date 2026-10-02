# gosec

**Version reviewed:** v2.29.0 ([official release](https://github.com/securego/gosec/releases/tag/v2.29.0)); metadata checked 2026-10-02.

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** Apache-2.0

[GitHub: securego/gosec](https://github.com/securego/gosec) · [Documentation](https://securego.io/)

## What it is for

Security checks for Go code: injection, weak crypto, unsafe file and network use.

Specialized for Go and aware of Go idioms, so it finds things generic rules miss. Run it next to Semgrep on Go services.

## Install

**Go (needs Go 1.25+)**

```bash
go install github.com/securego/gosec/v2/cmd/gosec@v2.29.0
```

**Container image**

```bash
docker pull ghcr.io/securego/gosec:latest
```

## Use

**Scan all packages**

```bash
gosec ./...
```

**SARIF output**

```bash
gosec -fmt sarif -out gosec.sarif ./...
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
gosec:
  stage: test
  image:
    name: ghcr.io/securego/gosec:latest
    entrypoint: [""]
  script:
    - gosec -fmt sarif -out gosec.sarif ./...
  artifacts:
    when: always
    paths: [gosec.sarif]
```

## Output and triage

Exit code 1 on any unsuppressed finding; `-no-fail` always returns 0. Suppress a reviewed line with `#nosec G104 -- reason`.

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
- [Find Security Bugs](find-sec-bugs.md) — SpotBugs plugin with security detectors for Java, Kotlin, and JVM frameworks.
- [eslint-plugin-security](eslint-security.md) — ESLint rules for risky JavaScript and TypeScript patterns.
- [mobsfscan](mobsfscan.md) — Source code checks for Android and iOS apps with native GitLab SAST output.
- [SonarQube](sonarqube.md) — Code quality and security server with quality gates and per-branch dashboards.
