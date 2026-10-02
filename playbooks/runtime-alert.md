# Runtime alert response

**Trigger:** Falco or endpoint activity requiring investigation.
**Owner:** platform/endpoint owner with the incident lead. Prerequisites:
restricted logs, deployment inventory, read-only investigation access and a
documented containment/rollback procedure.

1. Preserve UTC time, raw alert, rule/version, node/container ID, process/parent,
   user, file/socket path and available workload metadata. Link image digest,
   deployment revision and asset owner. Do not paste secrets into tickets.
2. Correlate exec/operator audit logs, CI changes, identity activity, neighboring
   workloads and network telemetry. An approved debug session can cause the same
   alert. Syscall process names alone cannot identify the human actor.
3. For active compromise, declare an incident and follow
   [incident response](incident-response.md). Preserve evidence when practical;
   choose containment with the service owner: credential revocation, network
   isolation or a controlled redeploy from a verified image. Inspect the node
   and runtime when socket access or escape is plausible.
4. Rotate exposed identities, assess reachable data, remove the entry path and
   investigate persistence. Rebuilding only the container may leave a compromised
   node, cloud credential or neighboring service untreated.
5. For expected behavior, record a scoped exception with owner, approver, reason,
   expiry and test. Validate with `dso exceptions`; Falco requires manual removal
   and reload for expiry. Test nearby unapproved behavior still alerts.
6. Verify service health and detection delivery, watch for recurrence, record the
   decision and corrective actions. Link evidence to `LOG-03` and `IR-01`.

Use [Falco triage](../rules/falco/triage.md) and
[rule limitations](../rules/falco/rule-catalog.json) during the investigation.
