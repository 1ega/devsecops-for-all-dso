# Kyverno

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0  
**Recommended first choice in this topic.**

[GitHub: kyverno/kyverno](https://github.com/kyverno/kyverno) · [Documentation](https://kyverno.io/docs/) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/policies/kubernetes/kyverno-policies)

## What it is for

Admission controller with policies written as Kubernetes YAML or CEL.

No new language to learn, and the full community policy library is imported in this repository. The CLI tests the same policies in CI before they reach a cluster.

> [!WARNING]
> The Kyverno CLI image has no shell; install the CLI in a shell image for GitLab jobs.

## Install

**Controller (Helm)**

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
kubectl create namespace kyverno
helm install kyverno --namespace kyverno kyverno/kyverno
```

## Use

**Apply policies to manifests offline**

```bash
kyverno apply policies/ --resource k8s/deployment.yaml
```

**Run policy tests (kyverno-test.yaml)**

```bash
kyverno test .
```

## Output and triage

Start every policy with `validationFailureAction: Audit`, read the PolicyReports, then switch to `Enforce`. Test policies against a live cluster with Chainsaw.

## Concepts to know

- Admission control
- Pod Security Standards
- RBAC
- Network policies
- Audit first, then enforce
- Managed Kubernetes
- GitOps

## Related tools

- [Chainsaw](chainsaw.md) — End-to-end tests for policies and controllers against a real cluster.
- [Gatekeeper](gatekeeper.md) — OPA-based admission controller with Rego constraint templates.
- [kube-linter](kube-linter.md) — Static checks for manifests and Helm charts before deploy.
- [Kubescape](kubescape.md) — Scans manifests and clusters against NSA, MITRE, and CIS frameworks.
- [kube-bench](kube-bench.md) — Checks cluster nodes against the CIS Kubernetes Benchmark.
