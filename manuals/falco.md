# Falco

**Versions:** Falco 0.45.0, Helm chart 9.2.0, rules 5.2.0, container plugin 0.7.4.
**License:** Apache-2.0 for Falco; MIT for our rules.
[Upstream](https://github.com/falcosecurity/falco) ·
[Helm documentation](https://falco.org/docs/setup/kubernetes/).

## What it is for

Falco detects suspicious process and file activity in running Linux containers.
Use the local rules to identify behaviors such as unexpected shells and access
to sensitive files, then route alerts to an assigned responder for triage.

## Prerequisites

Use supported Linux nodes with kernel/BTF support for `modern_ebpf`. The example
requests the chart's least-privileged capabilities; confirm your node OS supports
them. Windows nodes and serverless products without kernel access need separate
detection. This DaemonSet does not cover employee macOS/Windows endpoints:
see [osquery](osquery.md) and [Wazuh](wazuh.md).

Assign a platform owner, responder and destination. Review host mounts, runtime
sockets and capabilities in the rendered chart. Use a dedicated sensor namespace;
application Restricted Pod Security settings may prevent the required sensor
capabilities. Keep application namespaces restricted.

## Install and verify

Run from the repository root. The quoted `--set-file` argument actually loads
our rules and preserves the dot in the ConfigMap filename.

```bash
bash rules/falco/validate.sh
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm template falco falcosecurity/falco --version 9.2.0 -n falco \
  -f rules/falco/helm/values.yaml \
  --set-file 'customRules.dso-runtime\.yaml=rules/falco/dso-runtime.yaml' \
  > /tmp/falco-rendered.yaml
# Review images, privileges, mounts, plugins and the rule ConfigMap.
helm upgrade --install falco falcosecurity/falco --version 9.2.0 \
  -n falco --create-namespace -f rules/falco/helm/values.yaml \
  --set-file 'customRules.dso-runtime\.yaml=rules/falco/dso-runtime.yaml'
kubectl rollout status daemonset/falco -n falco --timeout=180s
kubectl get pods -n falco -o wide
kubectl logs -n falco -l app.kubernetes.io/name=falco --all-containers --tail=100
```

Compare desired/ready DaemonSet counts with all intended Linux nodes. Verify the
local rule file and plugins in startup logs; investigate every compile error.
Run the [isolated smoke test](../rules/falco/tests/README.md) on a Linux test host,
then a harmless interactive shell in a dedicated staging workload. Verify the
alert reaches the responder; record event/delivery times, node, rule, owner and
ticket as `LOG-03` evidence. No alert is a failed acceptance test.

## Routing and log protection

The example emits JSON to stdout. Forward it through your existing log collector,
or enable Falcosidekick with the [routing overlay](../skills/detection-response/runtime-security/examples/runtime-security/falcosidekick-values.yaml).
The chart configures **HTTP output**, so gRPC is unnecessary. Use
`falcosidekick.extraEnvFrom` with an existing Secret and supported environment
names such as `SLACK_WEBHOOKURL`; check the bundled sidekick chart. Avoid secrets
in CLI arguments, public values, shell history or exported Helm releases.
Keep services internal; the UI is disabled. Restrict sensor-to-router and
router-to-destination access. Test failed delivery and retained evidence.

Our rules omit command lines and file contents; upstream outputs may include
arguments and identifying data. Restrict log access and document retention.
Do not send generic suspicious events directly to automatic workload deletion.

## Tuning and maintenance

`rule_matching: all` prevents overlapping defaults hiding local detections;
account for CPU and duplicate alerts. `priority: notice` includes package-manager
execution; raising it to `warning` hides NOTICE. Priorities do not prove compromise.
The local rules require no upstream macros or plugin-specific fields. Runtime
container/image metadata still depends on collector configuration.

Load a private copy of [exceptions.example.yaml](../rules/falco/exceptions.example.yaml)
after the local rules. Match approved executable and parent tuples; add workload
context where available. Record owner, reason, approver and expiry using
[`dso exceptions`](../tools/dso/README.md). Falco does not expire exceptions itself:
remove expired overlays, validate, reload and re-test both allowed and nearby
unapproved activity. Avoid blanket namespace, image or process-name allowlists.

Monitor sensor readiness, kernel drops, output queue errors, rule counters and
memory. Connect your monitoring stack to the internal metrics endpoint. Review
coverage after every node-image change; review chart, engine, plugins and rules
upgrades together. Artifact following is disabled. Use `helm history falco -n
falco` and `helm rollback falco REVISION -n falco` for a reviewed rollback and
repeat the alert-delivery test.

## Troubleshoot

| Symptom | Check |
| :--- | :--- |
| No local alerts | Rule ConfigMap/mount, startup log, priority, overlapping rules |
| Unknown filter | Engine/plugin compatibility; compile errors must fail |
| Missing namespace/image | Runtime socket paths, container plugin, metadata availability |
| Uncovered nodes | Taints/selectors, node OS, BTF/capabilities, ready counts |
| Drops/OOM | Event rate, CPU throttling, buffers, expensive rules, resources |
| Router silent | HTTP output, service/DNS/network access, sidekick logs, destination secret |

Syscalls do not cover cloud IAM changes, Kubernetes API activity or application
business logic. Collect those logs separately; see [logging](../guides/logging-and-detection.md).

References: [fields](https://falco.org/docs/reference/rules/supported-fields/),
[exceptions](https://falco.org/docs/concepts/rules/exceptions/),
[matching](https://falco.org/docs/concepts/rules/style-guide/) and
[chart](https://github.com/falcosecurity/charts/tree/master/charts/falco).
