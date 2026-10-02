# GitHub Actions starter scans

Copy this caller into the application repository, replacing `FULL_COMMIT_SHA`
with a reviewed 40-character commit of this repository (or of your reviewed fork).

```yaml
name: Security
on: [push, pull_request]
permissions:
  contents: read
jobs:
  security:
    uses: 1ega/devsecopsforall/.github/workflows/security.yml@FULL_COMMIT_SHA
    with:
      run_secrets: true
      run_sca: true
      run_sast: true
```

Ubuntu hosted runner and Docker/network access are required. The workflow pins
scanner image digests, uses read-only source mounts and produces separate SARIF
artifacts retained seven days. Semgrep runs the registry `p/default` ruleset with
metrics off. Secrets block; SAST/SCA findings are report-only.
Tool failures and missing reports fail. Keep secrets out of this untrusted PR
job; deploy from a separate reviewed, protected workflow with scoped OIDC.

Enable the required status check after testing it. See the
[CI hardening guide](../../guides/cicd-hardening.md) and
[workflow](../../.github/workflows/security.yml).

For IaC and an optional public image digest, call [infrastructure.yml](../../.github/workflows/infrastructure.yml) with `image_digest: registry.example/app@sha256:DIGEST` after substituting an actual digest. Trivy 0.75.0 blocks HIGH/CRITICAL misconfiguration/vulnerabilities/secrets and scanner failures. Private registry authentication is environment-specific and is not passed to untrusted PR jobs by this template.
