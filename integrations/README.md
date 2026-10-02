# Starter integrations

| Integration | Entry point | Behavior |
| :--- | :--- | :--- |
| GitHub Actions | [Reusable workflow](github-actions/README.md) | Pinned Docker scanners, SARIF artifacts |
| GitLab CI | [Include](gitlab-ci/README.md) | Same starter secrets/SCA/SAST checks |
| pre-commit | [Hook config](pre-commit/README.md) | Pinned Gitleaks hook |
| DefectDojo | [Design notes](defectdojo/README.md) | Upload/deduplication still unimplemented |

Also planned: Jira tickets from findings, Slack alerts for critical findings and merge request comments.

Gitleaks blocks findings; OSV/Semgrep produce findings for triage and scanner
errors fail the job. This is not a normalized severity/delta gate. Network is
needed for images, OSV data and Semgrep registry rules. Secret scanning covers
the current tree; run a separate full-history scan as described in the manual.
Reports may contain sensitive code or paths; use private artifacts and retention.

Templates scan the caller repository; no production credentials are needed.
The repository's own validation compiles Falco rules separately. Test detection
and failure paths in your application before making jobs required.

A separate normalized gate is available for [GitHub Actions](github-actions/README.md#normalized-finding-gate) and [GitLab CI](gitlab-ci/README.md#normalized-finding-gate), using the shared [DSO CLI](../tools/dso/README.md). It supports reviewed baselines and blocks incomplete scans. The starter SARIF jobs described above retain their existing behavior.
