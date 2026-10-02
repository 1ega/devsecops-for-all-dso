# eslint-plugin-security

**Area:** 1. Protect your code → Static code analysis (SAST)  
**License:** Apache-2.0

[GitHub: eslint-community/eslint-plugin-security](https://github.com/eslint-community/eslint-plugin-security) · [Documentation](https://github.com/eslint-community/eslint-plugin-security#readme)

## What it is for

ESLint rules for risky JavaScript and TypeScript patterns.

Runs inside the linter developers already use, so findings appear in the editor. Expect noise: the rules warn on patterns that need a human look.

## Install

**npm**

```bash
npm install --save-dev eslint-plugin-security
```

## Use

**eslint.config.js (flat config)**

```js
const pluginSecurity = require('eslint-plugin-security');

module.exports = [pluginSecurity.configs.recommended];
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
eslint-security:
  stage: test
  image: node:22
  script:
    - npm ci
    - npx eslint . --max-warnings 0
```

## Output and triage

All recommended rules are warnings, so CI only fails with `--max-warnings 0` or when you raise rules to errors.

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
- [mobsfscan](mobsfscan.md) — Source code checks for Android and iOS apps with native GitLab SAST output.
- [SonarQube](sonarqube.md) — Code quality and security server with quality gates and per-branch dashboards.
