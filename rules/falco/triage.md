# Falco alert triage

1. Capture event time, rule name, priority, host, namespace, pod, container image digest, process tree, and the alert's original output. Store sensitive evidence in an approved case system.
2. Confirm whether the workload, deployment, and process are expected. Compare with the deployment change log and workload owner; do not dismiss an alert solely because it is frequent.
3. For a likely compromise, follow the [incident response skill](../../skills/detection-response/incident-response/SKILL.md): preserve evidence, contain the workload using an approved procedure, rotate exposed credentials, and investigate related nodes and images.
4. For a false positive, document the known behavior, owner, rule and exception scope, and review date. Test that the exception suppresses only the known activity. Keep the original alert record.
5. Close the case with a finding or false-positive decision and a rule change or follow-up task. Re-run a safe test event after tuning.
