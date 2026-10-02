# Research: gaps after the rule imports

**Reviewed:** 2026-10-02; this working tree, without production access.
Complements the [project survey](open-source-map.md).

The repo already has broad imported rules/policies and 91 initial manuals.
Before this change, Falco had three unvalidated examples, an unpinned install,
empty `customRules`, and obsolete gRPC routing advice. CI tested three Python
rules; integrations and playbooks were scaffolds. The rule directory move also
left stale roadmap links.

| Gap | Addition | Boundary |
| :--- | :--- | :--- |
| Runtime rules | 16 original rules, pinned engine/chart/artifacts, compiler and smoke harness | Live validation requires Linux Docker |
| Company evidence | Baseline inventory/assessment and `dso` | Owner assertions, no provider verification |
| Repeatable CI | GitHub/GitLab and pre-commit | SAST/SCA report-only; no normalized delta gate |
| Response | Incident/leak/dependency/triage/runtime/restore playbooks | Adopt private contacts, scope and deadlines |
| Recovery | Restic manual and restore evidence | DB-consistent/offsite/immutable design is environment-specific |
| Endpoints | osquery and Wazuh manuals | Telemetry and prevention differ; operate and size agents |
| SaaS | SCuBA manual | Permissions and unsupported settings need manual review |
| Application logic | Authorization test matrix | Integrate real application fixtures |

Primary sources: [NIST SMB CSF](https://www.nist.gov/itl/smallbusinesscyber/nist-cybersecurity-framework-0),
[CISA SMB](https://www.cisa.gov/small-and-medium-sized-business-resources),
[SCuBA](https://github.com/cisagov/ScubaGear),
[Falco rules](https://falco.org/docs/concepts/rules/),
[Restic](https://restic.readthedocs.io/en/stable/),
[osquery](https://osquery.readthedocs.io/en/stable/deployment/remote/),
[Wazuh](https://documentation.wazuh.com/current/quickstart.html).
Additions are original; no new third-party rule pack is copied.

Still open: mobile/imported rule CI coverage, Sigma/log-field mappings, cloud
evidence collectors, DefectDojo upload/deduplication, authenticated DAST,
application fixtures, signing/admission negative tests and additional scanner
acceptance fixtures. Device management, email/domain takeover, TLS expiry, external
exposure, vendor access and data retention need company-specific owners and
services. Do not label these completed just because a manual exists.

## Broader manual and code review

Fixed ZAP's unconditional error suppression, Semgrep's mixed-engine config path,
unredacted Gitleaks examples and mutable starter scanner/action references.
The Cosign example now actually passes the issued OIDC token and consumes the
build's immutable image reference; the earlier `docker inspect` expected a
locally pulled image and its identity token was unused. DefectDojo guidance now
requires a matching scope and deliberately selected closure settings. Added
Trivy IaC/image configs and runner templates, Kubernetes starter templates,
cloud evidence mapping, finding ownership/deadlines and Grype/Trivy wrapper tests.
Seven manual install/CI recipes now use release asset SHA256 checks instead of
executing mutable remote scripts; Trivy's Linux install is pinned as well.
YAML fences are parsed and accidental mapping/null GitLab commands rejected.
The full-tree check also repaired mislabeled HCL/text examples, malformed supply
chain/incident fragments, duplicate documentation keys and long-form SAM references.
Credential containment preserves legitimate MFA and handles issued sessions
separately from disabling a long-lived key.

Locally verified: Python starter Semgrep rules 3/3, evidence/exception/wrapper
tests, repository contracts, GitHub workflow syntax, Helm rendering with all 16
local rules, and Trivy 0.75.0 detecting the insecure Terraform fixture while the
restricted fixture passes. Trivy used an existing checks bundle, so this verifies
behavior rather than proving current vulnerability-data freshness. Falco compiler
and live smoke tests remain unexecuted locally because Docker is unavailable.
Other generated manuals and imported packs still need per-tool acceptance
testing; this review does not claim universal CI or deployed coverage.
