# Scanners

Ready-to-use configurations for third-party scanners: which checks are enabled, documented exceptions, custom rules, and the command that produces SARIF or JSON for [reporting](../reporting/README.md). Semgrep rule packs live in [`semgrep-rules/`](../semgrep-rules/README.md); standalone utilities written for this repository live in [`tools/`](../tools/README.md).

| Directory | Covers | Tool |
| :--- | :--- | :--- |
| [gitleaks](gitleaks/README.md) | Secrets in code and git history | gitleaks |
| [osv-scanner](osv-scanner/README.md) | Vulnerable dependencies in lockfiles | osv-scanner |
| [trivy](trivy/README.md) | Images, filesystems, misconfiguration | Trivy |
| [zap](zap/README.md) | Dynamic testing of web apps and APIs | OWASP ZAP |
| [nuclei](nuclei/README.md) | Template-based checks for exposed services | nuclei |
| [mobsf](mobsf/README.md) | Built APK, AAB, and IPA files | MobSF |

Each configuration should pin the tool version, explain every disabled check or allowlist entry, and include a small synthetic fixture that shows the expected result.

**Status:** Structure only; no scanner configurations are published yet.
