# Kubescape

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0  
**Notes:** Upstream GitLab CI guide; GitLab SAST output

[GitHub: kubescape/kubescape](https://github.com/kubescape/kubescape) · [Documentation](https://kubescape.io/docs/)

## What it is for

Scans manifests and clusters against NSA, MITRE, and CIS frameworks.

Gives a compliance-style score per framework and works both on files in CI and on live clusters.

## Install

**Homebrew or script**

```bash
brew install kubescape
# or
curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
```

## Use

**Scan manifests**

```bash
kubescape scan k8s/
```

**Scan the current cluster against NSA guidance**

```bash
kubescape scan framework nsa --compliance-threshold 80
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
kubescape:
  stage: test
  image: alpine:3.20
  before_script:
    - apk add --no-cache bash curl gcompat
    - curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
    - export PATH=$PATH:$HOME/.kubescape/bin
  script:
    - kubescape scan . --format gitlab-sast --output gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
```

## Output and triage

Exit code 1 when `--compliance-threshold` or `--severity-threshold` is not met.

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
- [kube-bench](kube-bench.md) — Checks cluster nodes against the CIS Kubernetes Benchmark.
