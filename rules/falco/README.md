# Falco runtime detection

**Status:** Deployment examples and an alert triage runbook. The shared examples are a starting point for a cluster; they require review and tuning before production use.

Falco watches runtime activity on hosts and Kubernetes nodes. Start with the [full manual](../../manuals/falco.md), then review the existing [Helm values and example rules](../../skills/detection-response/runtime-security/examples/runtime-security/README.md). This directory is the stable entry point for detection operators.

## Roll out

1. Choose the nodes and namespaces to monitor, and confirm the Falco driver and permissions required by your cluster.
2. Inspect [`falco-values.yaml`](../../skills/detection-response/runtime-security/examples/runtime-security/falco-values.yaml) and [`falco-custom-rules.yaml`](../../skills/detection-response/runtime-security/examples/runtime-security/falco-custom-rules.yaml). Test custom rules against your Falco version; keep vendor defaults enabled while tuning exceptions.
3. Install a pinned Falco Helm chart with reviewed values in a test cluster. Route alerts through [Falcosidekick values](../../skills/detection-response/runtime-security/examples/runtime-security/falcosidekick-values.yaml) to a monitored destination. Supply webhook or chat credentials through your secret manager, never this repository.
4. Generate one authorized test event, verify it reaches the destination, and follow the [triage runbook](triage.md). Record alert latency, noise, owner, and escalation route.

Example commands from the repository root:

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm upgrade --install falco falcosecurity/falco -n falco --create-namespace \
  -f skills/detection-response/runtime-security/examples/runtime-security/falco-values.yaml
kubectl logs -n falco -l app.kubernetes.io/name=falco --tail=100
```

Use `falco -V <rules-file>` with the deployed Falco version to validate rules before roll out. Falco [loads local rules after defaults](https://falco.org/docs/concepts/rules/default-custom/); check rule and chart compatibility together.
