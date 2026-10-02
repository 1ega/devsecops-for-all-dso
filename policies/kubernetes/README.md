# Kubernetes

Admission policies that keep unsafe workloads out of a cluster — privileged pods, root users, writable root filesystems, missing resource limits, untrusted registries — and audits of running clusters. New policies start in audit mode and move to enforce once tuned.

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| Kyverno | [kyverno/kyverno](https://github.com/kyverno/kyverno) | YAML policies; validate, mutate, verify images |
| Gatekeeper | [open-policy-agent/gatekeeper](https://github.com/open-policy-agent/gatekeeper) | Rego policies |
| kube-bench | [aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench) | CIS Kubernetes Benchmark |
| Kubescape | [kubescape/kubescape](https://github.com/kubescape/kubescape) | NSA and MITRE frameworks |
| Polaris | [FairwindsOps/polaris](https://github.com/FairwindsOps/polaris) | Workload best practices |

Related skills: [kyverno](../../skills/kubernetes-containers/kyverno/SKILL.md), [opa](../../skills/kubernetes-containers/opa/SKILL.md), [kubernetes-hardening](../../skills/kubernetes-containers/kubernetes-hardening/SKILL.md).

Imported: [kyverno-policies](kyverno-policies/SOURCE.md) (the full Kyverno community library with Chainsaw tests) and [gatekeeper-library](gatekeeper-library/SOURCE.md) (constraint templates with allowed and denied samples). Start from these and keep local changes in a separate directory so upstream updates stay easy.

Original [starter templates](starter/README.md): Restricted Pod Security, hardened workload, default network denial and explicit DNS allowance. Review placeholders and test CNI enforcement before adoption.

**Status:** Policy libraries imported and starter templates published; tuned admission policies of our own are not published yet.
