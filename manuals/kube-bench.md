# kube-bench

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0

[GitHub: aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench) · [Documentation](https://github.com/aquasecurity/kube-bench/blob/main/docs/running.md)

## What it is for

Checks cluster nodes against the CIS Kubernetes Benchmark.

The standard evidence for a CIS audit of your clusters. Platform-specific jobs exist for EKS, GKE, and AKS.

## Install

**Run as a Job in the cluster**

```bash
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job/kube-bench
```

## Use

**Use the job for your platform**

```bash
# job-eks.yaml, job-gke.yaml, job-aks.yaml in the repository
```

## Output and triage

Results are in the pod logs; edit the job command to `["kube-bench", "--json"]` for machine-readable output. `--exit-code` makes FAIL results return a non-zero code.

## Concepts to know

- Admission control
- Pod Security Standards
- RBAC
- Network policies
- Audit first, then enforce
- Managed Kubernetes
- GitOps

## Related tools

- [Kyverno](kyverno.md) — Admission controller with policies written as Kubernetes YAML or CEL.
- [Chainsaw](chainsaw.md) — End-to-end tests for policies and controllers against a real cluster.
- [Gatekeeper](gatekeeper.md) — OPA-based admission controller with Rego constraint templates.
- [kube-linter](kube-linter.md) — Static checks for manifests and Helm charts before deploy.
- [Kubescape](kubescape.md) — Scans manifests and clusters against NSA, MITRE, and CIS frameworks.
