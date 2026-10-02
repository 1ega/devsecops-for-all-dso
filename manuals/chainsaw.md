# Chainsaw

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0

[GitHub: kyverno/chainsaw](https://github.com/kyverno/chainsaw) · [Documentation](https://kyverno.github.io/chainsaw/latest/)

## What it is for

End-to-end tests for policies and controllers against a real cluster.

Proves a policy actually blocks what it should, in a kind cluster in CI, before you enforce it in production.

## Install

**Homebrew (use the tap; core has an unrelated chainsaw)**

```bash
brew tap kyverno/chainsaw https://github.com/kyverno/chainsaw
brew install kyverno/chainsaw/chainsaw
```

## Use

**Run the tests in the current directory**

```bash
chainsaw test
```

## Output and triage

Write JUnit with `--report-format JUNIT-TEST` to show results in GitLab.

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
- [Gatekeeper](gatekeeper.md) — OPA-based admission controller with Rego constraint templates.
- [kube-linter](kube-linter.md) — Static checks for manifests and Helm charts before deploy.
- [Kubescape](kubescape.md) — Scans manifests and clusters against NSA, MITRE, and CIS frameworks.
- [kube-bench](kube-bench.md) — Checks cluster nodes against the CIS Kubernetes Benchmark.
