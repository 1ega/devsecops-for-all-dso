# Logging and detection acceptance

Choose a log owner, responder, retention policy and restricted evidence store.
Use synchronized UTC clocks and account/cluster/environment/asset identifiers.

| Source | Minimum events | Acceptance test |
| :--- | :--- | :--- |
| Identity/SaaS | Admin/MFA changes, OAuth apps, anomalous sign-ins, forwarding | Reviewed test admin change reaches responder |
| Cloud | IAM/key changes, public exposure, disabled audit logs | Harmless tagged change appears centrally |
| Kubernetes audit | Exec, role changes, secret access, privileged workloads | Staging exec logged with actor and pod |
| Falco | Local and upstream rules on intended Linux nodes | Smoke test and routed staging event |
| Endpoints | Agent status, malware/FIM/process events for each OS | Harmless test file change and agent loss alert |
| Applications | Login failures, admin actions, authorization denial, rate limits | Denied cross-tenant request with correlation ID |
| CI/releases | Protected release decisions, artifact digest and signer | Release traced to commit/workflow/image |
| Backups | Failures, snapshot age, failed restore | Failure notification and isolated restore |

Avoid raw credentials, tokens, session cookies and personal request bodies.
Review command-line outputs for accidental secrets. Separate evidence-store
access and use immutability where supported. Define ingestion-delay objectives.
Check missing sources and agents daily; silent telemetry is a coverage incident.
Deduplicate by rule/asset/time window while retaining original evidence.

Keep a detection register: name, source, owner, positive/negative test, last test,
priority, destination, escalation and exceptions. Re-test after collector, node,
credential or routing changes. Also test stopped sensors and failed forwarding.
Falco syscall rules do not ingest provider or Kubernetes API logs automatically.

See [triage](../rules/falco/triage.md), [Wazuh](../manuals/wazuh.md) and
[incident response](../playbooks/incident-response.md).
