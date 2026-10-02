# Semgrep profiles

Ready-made rule selections so a project does not have to pick rules by hand.

| Profile | Includes | Use it for |
| :--- | :--- | :--- |
| `ci-blocking` | `ERROR` rules with `confidence: HIGH` | Merge request gates that fail the build |
| `pr-diff` | `ci-blocking` plus `WARNING`, changed files only | Review comments on a merge request |
| `audit` | Every rule, including `INFO` | Scheduled scans and manual audits |

Profiles depend on consistent rule metadata; see [severity-and-metadata.md](../../../reporting/severity-and-metadata.md).

**Status:** Structure only; no profiles are published yet.
