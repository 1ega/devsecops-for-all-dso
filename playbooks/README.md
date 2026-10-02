# Response and recovery playbooks

Adapt contacts, authority, time objectives and evidence storage in a private copy.
The incident lead decides changes to live services using the documented process.

| Playbook | Trigger |
| :--- | :--- |
| [Incident response](incident-response.md) | Suspected compromise or serious security impact |
| [Leaked secret](leaked-secret.md) | Credential in code, logs or public artifacts |
| [Compromised dependency](compromised-dependency.md) | Hijacked/malicious package, action or image |
| [Vulnerability triage](vulnerability-triage.md) | Scanner/provider finding needing a decision |
| [Runtime alert](runtime-alert.md) | Falco or endpoint suspicious activity |
| [Restore drill](restore-drill.md) | Scheduled recovery test or major backup change |

Retain owner, timeline, affected assets, decisions, changes and recovery evidence.
Risk acceptance requires a named approver, compensating control and expiry; use
[`dso exceptions`](../tools/dso/README.md). Test a tabletop and a restore before
an emergency. See [baseline](../baseline/README.md) and
[logging acceptance](../guides/logging-and-detection.md).

**Status:** Original starter procedures are published; production contacts and
company-specific response actions must be completed by the adopting team.
