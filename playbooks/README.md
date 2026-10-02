# Playbooks

Operational response procedures belong here. A playbook should state its trigger, prerequisites, roles, decision points, evidence to retain, recovery steps, and verification. Clearly distinguish preparation from actions that change live systems.

Planned playbooks:

| Playbook | Trigger |
| :--- | :--- |
| Leaked secret | A secret scanner finding or an external report of an exposed credential |
| Compromised dependency | A malicious or hijacked package, image, or action in use |
| Vulnerability in production | A confirmed exploitable finding in a deployed service |
| Cloud misconfiguration | Public data, an overly broad IAM grant, or disabled logging found in a live account |
| Finding triage | Deciding true or false positive, risk acceptance, and remediation deadlines by severity |

Related skills: [incident-response](../skills/detection-response/incident-response/SKILL.md), [supply-chain-attack-response](../skills/supply-chain/supply-chain-attack-response/SKILL.md), [kingfisher](../skills/secrets-management/kingfisher/SKILL.md).

**Status:** Structure only; no playbooks are published yet.
