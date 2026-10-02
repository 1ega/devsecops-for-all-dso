# Scanners

Ready-to-use configurations for third-party scanners: which checks are enabled, documented exceptions, custom rules, and the command that produces SARIF or JSON for [reporting](../reporting/README.md). Semgrep rule packs live in [`semgrep-rules/`](../semgrep-rules/README.md); standalone utilities written for this repository live in [`tools/`](../tools/README.md).

| Directory | Covers | Tool |
| :--- | :--- | :--- |
| [gitleaks](gitleaks/README.md) | Secrets in code and git history | gitleaks |
| [secrets-patterns-db](secrets-patterns-db/SOURCE.md) | Imported database of secret patterns | — |
| [osv-scanner](osv-scanner/README.md) | Vulnerable dependencies in lockfiles | osv-scanner |
| [trivy](trivy/README.md) | Images, filesystems, misconfiguration | Trivy |
| [zap](zap/README.md) | Dynamic testing of web apps and APIs | OWASP ZAP |
| [nuclei](nuclei/README.md) | Template-based checks for exposed services | nuclei |
| [mobsf](mobsf/README.md) | Built APK, AAB, and IPA files | MobSF |
| [apkleaks](apkleaks/SOURCE.md) | Imported patterns for secrets and endpoints in APKs | apkleaks |

Each configuration should pin the tool version, explain every disabled check or allowlist entry, and include a small synthetic fixture that shows the expected result.

Imported upstream content keeps its license; each imported directory has a `SOURCE.md`. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

**Status:** Upstream reference content imported; no configurations of our own are published yet.
