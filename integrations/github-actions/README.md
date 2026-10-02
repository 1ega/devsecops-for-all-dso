# GitHub Actions

A reusable workflow (`workflow_call`) that runs the repository's checks in another project's pipeline. Each stage — Semgrep, secrets, dependencies, IaC — is switched on with an input, results are written as SARIF and uploaded to GitHub code scanning.

Planned contents:

- `security.yml` reusable workflow with inputs such as `semgrep`, `secrets`, `sca`, `iac` and `profile`.
- An example caller workflow for a consuming project.
- Notes on required `permissions:` (`contents: read`, `security-events: write`).

Pin every action by commit SHA and pin this repository to a tag, so rule updates do not change CI results unexpectedly. Audit the workflow itself with [zizmor](https://github.com/zizmorcore/zizmor) and [actionlint](https://github.com/rhysd/actionlint).

**Status:** Structure only; no workflow is published yet.
