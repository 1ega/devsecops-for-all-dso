# Scanners

Ready-to-use configurations for third-party scanners: which checks are enabled, documented exceptions, custom rules, and the command that produces SARIF or JSON for [reporting](../reporting/README.md). Rule sets used by these scanners, including Semgrep packs and secret patterns, live in [`rules/`](../rules/README.md); standalone utilities written for this repository live in [`tools/`](../tools/README.md).

| Directory | Covers | Tool |
| :--- | :--- | :--- |
| [gitleaks](gitleaks/README.md) | Secrets in code and git history | gitleaks |
| [osv-scanner](osv-scanner/README.md) | Vulnerable dependencies in lockfiles | osv-scanner |
| [grype](grype/README.md) | Vulnerabilities in filesystems, images, and SBOMs; SARIF and severity gate | Grype |
| [prowler](prowler/README.md) | AWS, Azure, GCP, and Kubernetes posture; JSON OCSF and HTML | Prowler |
| [trivy](trivy/README.md) | Images, filesystems, misconfiguration | Trivy |
| [zap](zap/README.md) | Dynamic testing of web apps and APIs | OWASP ZAP |
| [nuclei](nuclei/README.md) | Template-based checks for exposed services | nuclei |
| [mobsf](mobsf/README.md) | Built APK, AAB, and IPA files | MobSF |
| [osquery](osquery/README.md) | Scheduled endpoint inventory | osquery |

Each configuration should pin the tool version, explain every disabled check or allowlist entry, and include a small synthetic fixture that shows the expected result.

Imported upstream content keeps its license; each imported directory has a `SOURCE.md`. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

Use the [baseline](../baseline/README.md) and [finding lifecycle](../reporting/finding-lifecycle.md) to track coverage and ownership.

**Status:** Upstream reference content is imported. Grype, Prowler and Trivy contain local wrappers, Trivy also has configs and fixtures, and osquery has an inventory configuration; the other scanner directories vary in readiness, so check each README.
