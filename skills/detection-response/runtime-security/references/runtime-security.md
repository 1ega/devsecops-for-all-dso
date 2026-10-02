# Runtime security reference

Use the maintained [Falco manual](../../../../manuals/falco.md),
[rule pack](../../../../rules/falco/README.md),
[validation](../../../../rules/falco/tests/README.md) and
[response playbook](../../../../playbooks/runtime-alert.md).

Falco observes Linux syscalls through a node sensor. The supported example uses
modern eBPF and tested node capabilities/BTF, keeps upstream rules and loads
local rules explicitly. This is not provider IAM, Kubernetes API audit or
application authorization coverage. Serverless/restricted managed environments
need a separate supported collection approach; do not assume DaemonSet scheduling
means required kernel access is available.

Falcosidekick consumes HTTP JSON output. gRPC is deprecated in current Falco and
unnecessary for the chart's sidekick routing. Monitor sensor/node coverage,
kernel drops, output failures and metadata availability. Priority changes only
filter output; they are not a substitute for measuring engine load and drops.

Local rule names/path heuristics can be bypassed. Review the catalog's limits,
correlate API/identity logs, and use narrow dated exceptions. A Kyverno bridge
requires an authenticated external responder and explicit containment design;
it is not automatically provided by a runtime alert.
