# Integrations

Reusable ways to connect repository content to delivery workflows belong here: CI templates, local hooks, and the systems that receive findings.

| Directory | Purpose |
| :--- | :--- |
| [github-actions](github-actions/README.md) | Reusable workflow with SARIF upload to code scanning |
| [gitlab-ci](gitlab-ci/README.md) | CI template enabled with one `include:` |
| [pre-commit](pre-commit/README.md) | Fast local checks before a commit |
| [defectdojo](defectdojo/README.md) | Importing results into DefectDojo for tracking and deduplication |

Keep each integration self-contained with setup instructions, required permissions, an example, and a safe way to test it. Repository maintenance workflows remain in [`.github/workflows/`](../.github/workflows/).

**Status:** Structure only; no reusable integrations are published yet.
