# Wazuh: host detection and centralized security events

**Version covered:** 4.14.8; official deployment guide for 4.14.
**License:** components carry their own GPL/Apache licenses; review upstream.
[Upstream](https://github.com/wazuh/wazuh/releases/tag/v4.14.8) ·
[Quickstart](https://documentation.wazuh.com/current/quickstart.html).

Wazuh combines endpoint agents with a manager, indexer and dashboard for log
analysis, file integrity and host security visibility. Start with a test server
and a few endpoints, assigning someone to maintain agents, rules, storage and
alerts. A single-node pilot has a single point of failure.

## Install and enroll

Follow the official 4.14 package/installation guide, pinning server/indexer/
dashboard/agent versions to a compatible set. Verify downloaded packages and
inspect the installer before privileged execution. Size the host from measured
agent count, event rate and retention using the quickstart requirements.
Keep dashboard, enrollment and indexer ports private, use trusted TLS and replace
initial passwords. Store generated credentials in the secret manager.

Enroll one Linux and one Windows/macOS test endpoint using the dashboard's
OS-specific instructions. Record device ownership, agent ID, version and last
check-in. Review every configured collector before adding fleets.

## Acceptance and response

Enable file integrity monitoring for a dedicated test directory; create/change
a harmless file and verify the event, source host and notification destination.
Test agent loss and log-ingestion failure. Inspect manager/agent/indexer health
and retention. Confirm responder access while preventing ordinary users from
reading sensitive host evidence. Never use live malware as a smoke fixture.

Begin with alerts and human response; disable automatic active response until
specific actions, scope, rollback and false-positive behavior are tested.
Correlate with identity/cloud and [Falco](falco.md) events rather than assuming
host coverage includes Kubernetes API or SaaS audit data. Record acceptance in
`END-02`, `LOG-01/02`; use the [incident playbook](../playbooks/incident-response.md).

Sources: [architecture](https://documentation.wazuh.com/current/getting-started/index.html)
and [file integrity](https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/index.html).
