# kube-linter

**Version reviewed:** v0.8.3 ([official release](https://github.com/stackrox/kube-linter/releases/tag/v0.8.3)); metadata checked 2026-10-02.

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0

[GitHub: stackrox/kube-linter](https://github.com/stackrox/kube-linter) · [Documentation](https://docs.kubelinter.io)

## What it is for

Static checks for manifests and Helm charts before deploy.

Catches privileged containers, missing limits, and writable root filesystems in the merge request, without a cluster.

## Install

**Homebrew or Go**

```bash
brew install kube-linter
# or
go install golang.stackrox.io/kube-linter/cmd/kube-linter@v0.8.3
```

## Use

**Lint with SARIF output**

```bash
kube-linter lint --format sarif --output kube-linter.sarif k8s/
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
kube-linter:
  stage: test
  image:
    name: stackrox/kube-linter:v0.8.3-alpine@sha256:b8311611c27032d4922bc67719225e373e4a0ab0c767bbdcf5f20a9306b1a3bb   # the default tag has no shell
    entrypoint: [""]
  script:
    - /kube-linter lint --format sarif --output kube-linter.sarif k8s/
  artifacts:
    when: always
    paths: [kube-linter.sarif]
```

## Output and triage

Exits non-zero when a check fails. Tune checks in `.kube-linter.yaml`.

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
- [Kubescape](kubescape.md) — Scans manifests and clusters against NSA, MITRE, and CIS frameworks.
- [kube-bench](kube-bench.md) — Checks cluster nodes against the CIS Kubernetes Benchmark.
