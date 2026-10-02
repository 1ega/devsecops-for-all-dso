# Roadmap

The [published interactive roadmap](https://1ega.github.io/devsecopsforall/) is
part of this repository. Its current sources cover ten areas, 29 topics, 95 tool
manuals and all 32 [company baseline controls](baseline/README.md). Start with
[SMB adoption](guides/smb-security.md), then use [Find by task](README.md#find-by-task).
Tools supplement identity, devices, recovery and response; owning a manual or
marking a tool adopted does not establish a working control.

## Current repository coverage

| Need | Available now | Remaining acceptance or implementation |
| :--- | :--- | :--- |
| Company foundation | [32 controls](baseline/README.md), [inventory/evidence/exception CLI](tools/dso/README.md), owners and vendor/data review | Connect assertions to provider/device evidence; adopt private owners and scope |
| Workforce, SaaS and devices | [SCuBA](manuals/scuba.md), [osquery](manuals/osquery.md), [Wazuh](manuals/wazuh.md), identity/offboarding controls | Test tenant permissions, device enrollment, MFA recovery, OAuth/mail settings and agent loss |
| Recovery | [Restic](manuals/restic.md), [restore playbook](playbooks/restore-drill.md), RPO/RTO and isolated credentials | Run business/database-consistent offsite restore and immutability acceptance tests |
| Code and secrets | Original/imported [Semgrep packs](rules/semgrep/README.md), pinned [CI/pre-commit starters](integrations/README.md) | Mobile/elttam/Trail of Bits CI coverage, additional secret fixtures and reviewed blocking profiles |
| Dependencies, SBOMs and images | [Grype](scanners/grype/README.md)/[Trivy](scanners/trivy/README.md) wrappers, Trivy IaC fixtures, SBOM/signing manuals | Native scanner coverage/error fixtures, freshness checks, release signing/admission rejection tests |
| CI/CD | [GitHub/GitLab source and infrastructure jobs](integrations/README.md), [runner hardening](guides/cicd-hardening.md) | Caller-project acceptance; SAST/SCA remain report-only; normalized new-finding gates unimplemented |
| Infrastructure/Kubernetes | Imported libraries, [Restricted workload/network starters](policies/kubernetes/starter/README.md), Trivy fixtures | Cluster RBAC, privileged-pod rejection, allowed/denied network tests and expiring policy exceptions |
| Cloud, exposure and domains | [Prowler wrapper](scanners/prowler/README.md), [provider evidence map](policies/cloud/evidence-map.md), DNS/TLS/registrar controls | AWS/Azure/GCP evidence collectors and fixtures; deployed exposure and expiry-alert tests |
| Runtime and logs | [16 Falco rules and pinned Helm config](rules/falco/README.md), compiler/smoke harness, [log acceptance matrix](guides/logging-and-detection.md) | Rule-specific negative cases, staging node coverage, delivery/drop/failure tests; Sigma and log-field mappings |
| Apps and APIs | [ZAP](manuals/zap.md), [Schemathesis](manuals/schemathesis.md), [authorization matrix](guides/api-authorization.md) | Authenticated DAST and real cross-user/tenant/state fixtures; rate-limit/business-flow tests |
| Findings and incidents | [Finding lifecycle](reporting/finding-lifecycle.md), [expiring exceptions](reporting/exceptions.example.json), six [response/triage/restore playbooks](playbooks/README.md) | DefectDojo upload/deduplication/closure acceptance, provider-specific containment and tabletop evidence |
| Roadmap publishing | Cards generated from manuals; every manual/control needs a catalog entry; CI detects stale data and missing links | Publish reviewed changes through the Pages workflow and check the live map |

## Next delivery priorities

1. **Complete runtime acceptance.** CI compiles both local Falco files with 0.45.0
   on every push. The [test record](rules/falco/tests/README.md) reports 16/16
   positive rules and no negative alerts on a Docker Desktop Linux VM; rule-specific
   non-match scenarios remain unautomated. Test staging node coverage, alert
   delivery, missing nodes and failed output.
2. **Verify imported rule coverage and scanner failures.** Add CI for mobile,
   Trail of Bits and elttam rules. Cover synthetic secret, native Grype/image,
   YARA positive/negative and permission/database/error cases; retain coverage
   and rule/database-version context rather than treating missing results as clean.
3. **Finish the finding loop.** Add normalized severity/owner/SLA adapters,
   scoped DefectDojo import with deduplication and incomplete-scan closure tests,
   and gates for confirmed new findings. Keep expiring risk decisions separate
   from automatically applied suppressions.
4. **Test enforcement and application logic.** Exercise Kubernetes admission,
   network/RBAC and approved-signer checks in a disposable cluster. Add real API
   role/tenant fixtures and authenticated staging DAST. Retest deployed state.
5. **Operate the company controls.** Build read-only cloud/SaaS evidence
   collectors and log-field/Sigma mappings; test device/offboarding, domain/TLS,
   vendor access, backup recovery and incident response with private evidence.
   Add reproducible detection-and-fix labs beyond the current Trivy fixture.

## Validation and maintenance

The [repository review](docs/research/smb-operational-gaps.md) records existing
local checks and their limits. The [roadmap audit](docs/research/roadmap-sync.md)
records the online drift and the Falco compilation failure that CI now passes. Most manuals/imported packs
still require per-tool acceptance; generated coverage is not deployed coverage.

Edit manuals and [the topic catalog](tools/roadmap/catalog.json), then run
`python3 tools/roadmap/sync.py`. [CI](tools/roadmap/README.md) checks every manual,
control and repository resource and rejects stale site instructions. Keep tool
IDs stable so deep links and browser progress survive updates.

For each new control, include a [research note](docs/research/README.md), example
or fixture, expected outcome, tuning/response guidance, source/license details
and README entry. Follow the [contribution guide](CONTRIBUTING.md).
