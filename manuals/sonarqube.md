# SonarQube

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** LGPL-3.0 (Community Build)

[GitHub: SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) · [Documentation](https://docs.sonarsource.com/sonarqube-community-build/)

## What it is for

Code quality and security server with quality gates and per-branch dashboards.

Many teams already run it for code quality; its security rules and quality gates give developers one dashboard. Branch and pull request analysis need a commercial edition.

## Install

**Run the server (Community Build)**

```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:community
```

## Use

**Analyze a project with the scanner CLI**

```bash
docker run --rm -v "$PWD:/usr/src" \
  -e SONAR_HOST_URL="http://sonarqube.example.com" -e SONAR_TOKEN="$SONAR_TOKEN" \
  sonarsource/sonar-scanner-cli -Dsonar.projectKey=my-app
```

## Output and triage

Configure the project in `sonar-project.properties`. Findings can be exported to DefectDojo with its SonarQube parser.

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
- [mobsfscan](mobsfscan.md) — Source code checks for Android and iOS apps with native GitLab SAST output.
