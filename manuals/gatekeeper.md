# Gatekeeper

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0

[GitHub: open-policy-agent/gatekeeper](https://github.com/open-policy-agent/gatekeeper) · [Documentation](https://open-policy-agent.github.io/gatekeeper/website/docs/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/kubernetes/gatekeeper-library)

## What it is for

OPA-based admission controller with Rego constraint templates.

Choose it if your team already writes Rego for OPA or conftest. The constraint template library is imported in this repository.

## Install

**Controller (Helm)**

```bash
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm install gatekeeper/gatekeeper --name-template=gatekeeper \
  --namespace gatekeeper-system --create-namespace
```

**gator CLI**

```bash
brew install gator
```

## Use

**Test manifests against templates and constraints**

```bash
gator test -f=my-manifest.yaml -f=templates-and-constraints/
```

**Run test suites**

```bash
gator verify ./...
```

## Output and triage

`gator test` exits 1 on violations of constraints with `enforcementAction: deny`; `dryrun` constraints only report.

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
- [kube-linter](kube-linter.md) — Static checks for manifests and Helm charts before deploy.
- [Kubescape](kubescape.md) — Scans manifests and clusters against NSA, MITRE, and CIS frameworks.
- [kube-bench](kube-bench.md) — Checks cluster nodes against the CIS Kubernetes Benchmark.
