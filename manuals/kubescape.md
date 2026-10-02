# Kubescape

**Version reviewed:** v4.0.15 ([official release](https://github.com/kubescape/kubescape/releases/tag/v4.0.15)); metadata checked 2026-10-02.

**Area:** 6. Guard Kubernetes → Kubernetes admission and audit  
**License:** Apache-2.0  
**Notes:** Upstream GitLab CI guide; GitLab SAST output

[GitHub: kubescape/kubescape](https://github.com/kubescape/kubescape) · [Documentation](https://kubescape.io/docs/)

## What it is for

Scans manifests and clusters against NSA, MITRE, and CIS frameworks.

Gives a compliance-style score per framework and works both on files in CI and on live clusters.

## Install

**Verified release package (Linux amd64)**

The checksum below was read from the official release metadata on 2026-10-02.
Use the matching release asset/checksum for another OS or architecture.
SHA256 pinning checks integrity; review upstream signatures/provenance before
trusting a new release.

```bash
set -eu
curl --fail --show-error --location https://github.com/kubescape/kubescape/releases/download/v4.0.15/kubescape_4.0.15_linux_amd64 -o kubescape
printf '%s  %s\n' '011569dbcde85afc96cf63262e4f967166b6680fd70a623e9065334b6767b244' 'kubescape' | sha256sum --check -
sudo install -m 0755 kubescape /usr/local/bin/kubescape
```

On macOS, `brew install kubescape` is a convenient alternative; verify its installed
version before using it with a pinned CI setup.

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
  image: ubuntu:24.04@sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - |
      curl --fail --show-error --location https://github.com/kubescape/kubescape/releases/download/v4.0.15/kubescape_4.0.15_linux_amd64 -o kubescape
      printf '%s  %s\n' '011569dbcde85afc96cf63262e4f967166b6680fd70a623e9065334b6767b244' 'kubescape' | sha256sum --check -
      install -m 0755 kubescape /usr/local/bin/kubescape
  script:
    - kubescape scan framework nsa --compliance-threshold 80 . --format gitlab-sast --output gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
```

## Output and triage

A compliance score gate applies to framework/control scans and
`--view resource|control`; default security-view scans do not apply that score
threshold. Adopt and tune the sample score before gating. See the
[official scanning guide](https://kubescape.io/docs/scanning/).

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
