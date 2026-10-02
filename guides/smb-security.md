# Implement security in a small company

Name an accountable security owner and backup; a small team can combine roles.
Track assets, dated evidence and gaps with the [baseline](../baseline/README.md).
Choose a stack you can maintain: existing identity/device tooling, Gitleaks, one
SAST engine, one dependency/image scanner, provider logs, backups and a responder.
Add Kubernetes/Falco only when you operate supported Linux nodes.

| Outcome | Implementation | Acceptance evidence |
| :--- | :--- | :--- |
| Known assets | Inventory SaaS, domains, devices, accounts, repos, services, data | No unowned production asset |
| Strong identity | SSO/MFA, password manager, separate admins, recovery procedure | Policy export, MFA exception review, recovery test |
| Access removal | Joiner/mover/leaver checklist; short-lived workload credentials | Departed identity loses SaaS/cloud/repo access |
| Email/SaaS | OAuth-app and forwarding review, SPF/DKIM/DMARC rollout; [SCuBA](../manuals/scuba.md) | Tenant assessment and mail authentication test |
| Endpoints | MDM, encryption, patching, EDR where needed; [osquery](../manuals/osquery.md) | Coverage/patch export and lost-device procedure |
| Recovery | [Restic](../manuals/restic.md) or native backups with isolated credentials | [Restore drill](../playbooks/restore-drill.md) meets RPO/RTO |
| Code/builds | Reviews, minimal tokens, protected releases, secrets/SAST/SCA | [CI](../integrations/README.md) detects synthetic fixtures |
| Artifacts/IaC | Trivy, SBOM, signer verification and admission controls | Release digest/reports and negative policy test |
| Network/cloud | Private management access, least privilege, audit logging | Posture scan and deployed-state retest |
| Detection | [Logging](logging-and-detection.md), [Falco](../manuals/falco.md), optionally [Wazuh](../manuals/wazuh.md) | Test reaches responder; missing telemetry alerts |
| Applications | [Authorization matrix](api-authorization.md), secret store, rate limits | Cross-user/tenant/role tests |
| Response | [Playbooks](../playbooks/README.md), finding deadlines, expiring exceptions | Tabletop and remediation retest |

Record `not_applicable` with a reason for absent technology. A manual, installed
scanner or green CI alone does not establish an implemented control. Review
findings weekly and access/exceptions monthly; exercise restore and incident
response after major changes. Include operator time, log storage, database
downloads, routing and recovery in the budget.

Start existing SAST/SCA findings in report-only while assigning owners. Block
secret findings and tool failures immediately. After tuning, gate confirmed new
high-risk findings. The starter CI documents its behavior; a normalized delta
gate is still unimplemented.

Sources: [NIST small-business CSF guidance](https://www.nist.gov/itl/smallbusinesscyber/nist-cybersecurity-framework-0)
and [CISA SMB resources](https://www.cisa.gov/small-and-medium-sized-business-resources).
