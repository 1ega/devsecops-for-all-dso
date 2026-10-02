# Find Security Bugs

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** LGPL-3.0

[GitHub: find-sec-bugs/find-sec-bugs](https://github.com/find-sec-bugs/find-sec-bugs) · [Documentation](https://find-sec-bugs.github.io/)

## What it is for

SpotBugs plugin with security detectors for Java, Kotlin, and JVM frameworks.

Works on compiled bytecode, so it understands Spring, JAX-RS, and other frameworks deeply. Add it to the Maven or Gradle build you already have.

## Install

**Maven: add the plugin to spotbugs-maven-plugin**

```bash
<plugin>
  <groupId>com.github.spotbugs</groupId>
  <artifactId>spotbugs-maven-plugin</artifactId>
  <configuration>
    <plugins>
      <plugin>
        <groupId>com.h3xstream.findsecbugs</groupId>
        <artifactId>findsecbugs-plugin</artifactId>
        <version>1.14.0</version>
      </plugin>
    </plugins>
  </configuration>
</plugin>
```

## Use

**Run with Maven**

```bash
mvn compile spotbugs:check
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
find-sec-bugs:
  stage: test
  image: maven:3-eclipse-temurin-21
  script:
    - mvn -B compile spotbugs:check
  artifacts:
    when: always
    paths: [target/spotbugsXml.xml]
```

## Output and triage

Results are SpotBugs XML in `target/`. For Gradle setup and the full configuration, follow the project wiki linked from the documentation page.

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
- [eslint-plugin-security](eslint-security.md) — ESLint rules for risky JavaScript and TypeScript patterns.
- [mobsfscan](mobsfscan.md) — Source code checks for Android and iOS apps with native GitLab SAST output.
- [SonarQube](sonarqube.md) — Code quality and security server with quality gates and per-branch dashboards.
