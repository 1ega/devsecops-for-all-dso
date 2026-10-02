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

## Normalized finding gate

The separate [dso-gate workflow](../../.github/workflows/dso-gate.yml) runs
Gitleaks, the local Python Semgrep starter pack and offline Trivy dependency
checks through the [DSO CLI](../../tools/dso/README.md). It blocks findings at or
above `fail_on` (default `high`, which includes the Semgrep starter rules) and any
unknown severity, and fails incomplete scans. The existing SARIF workflow above
retains its behavior.

```yaml
name: DSO gate
on: [push, pull_request]
permissions:
  contents: read
jobs:
  security:
    uses: 1ega/devsecopsforall/.github/workflows/dso-gate.yml@FULL_COMMIT_SHA
    with:
      kit_ref: FULL_COMMIT_SHA
      # kit_branch: main         # protected kit branch that must contain kit_ref
      # fail_on: high            # info, low, medium, high or critical
      # Optional: a reviewed baseline from a protected caller branch.
      # baseline_ref: TRUSTED_CALLER_COMMIT_SHA
      # baseline_branch: main
      # baseline_path: .security/dso-baseline.json
```

Replace both kit references with the same reviewed 40-character commit. The job
fails unless `kit_ref` is reachable from `kit_branch` of the kit repository and
`baseline_ref` from `baseline_branch` of the caller repository, so a fork-only or
unreviewed commit cannot be selected. The caller checkout is scanned without
submodules or LFS objects; scan those separately if they hold code or secrets.
The target never supplies executable DSO code or kit rules, and the baseline comes
from a separate trusted checkout, not the PR branch.

Create the baseline from a completed report of the protected branch with project
`owner/repository` (the workflow's `--project`), review it and commit it to the
protected branch at `baseline_path`. A baseline from an older kit or another
engine is still compared; the gate lists such differences in `coverage_changes`,
and any new or escalated findings need review before the baseline is refreshed.
The normalized report (no secret values, but secret fingerprints and paths) is
kept as an artifact for seven days. Protect the workflow, kit reference and
baseline selection with review/branch rules; YAML cannot make its own policy
immutable. Caller-project acceptance and required-check configuration must be
tested in the consuming project.
