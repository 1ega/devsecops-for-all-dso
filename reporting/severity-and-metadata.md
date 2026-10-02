# Severity and metadata

**Status:** Draft. Agree on it before normalizing rule metadata or building CI gates.

Rules keep their native severity — Semgrep uses `ERROR`, `WARNING`, and `INFO`, as described in the [mobile rule pack](../rules/semgrep/mobile/README.md#adding-a-rule). Reports and CI gates use one normalized scale so results from different tools can be compared.

## Normalized scale

| Level | Meaning | Gate in the `ci-blocking` profile |
| :--- | :--- | :--- |
| `critical` | Direct exploitation, or a leaked secret or data | Fails the job |
| `high` | Likely vulnerability with significant impact | Fails the job when confidence is high |
| `medium` | Weakness that depends on context | Reported |
| `low` | Hardening or best practice | Reported |
| `info` | Item for manual review | Shown only in the `audit` profile |

## Mapping from tools

| Tool | Native value | Normalized |
| :--- | :--- | :--- |
| Semgrep | `ERROR` | `high` (`critical` when `impact: HIGH` and `confidence: HIGH`) |
| Semgrep | `WARNING` | `medium` |
| Semgrep | `INFO` | `low` or `info` |
| gitleaks | any finding | `critical` until triaged |
| Trivy, osv-scanner, Grype | `CRITICAL` / `HIGH` / `MEDIUM` / `LOW` | same level |
| ZAP | High / Medium / Low / Informational | `high` / `medium` / `low` / `info` |

## Rule metadata

Every security rule should carry:

```yaml
metadata:
  category: security
  cwe: "CWE-312: Cleartext Storage of Sensitive Information"
  confidence: HIGH | MEDIUM | LOW
  likelihood: HIGH | MEDIUM | LOW
  impact: HIGH | MEDIUM | LOW
  owasp: "A02:2021 - Cryptographic Failures"   # web and API rules
  masvs: MASVS-STORAGE-1                         # mobile rules
  references:
    - https://...
  source: <upstream project or local>
  license: <SPDX identifier>
```

`cwe`, `masvs`, and `owasp` drive the [compliance mapping](compliance-mapping/README.md); `confidence` and `impact` drive the CI profiles in [rules/semgrep/profiles](../rules/semgrep/profiles/README.md).
