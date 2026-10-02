# pre-commit

Hooks that give developers fast feedback before a commit leaves their machine: secret detection, a quick Semgrep profile, Dockerfile linting, and IaC linting. Only checks that finish in a few seconds belong here; full scans run in CI.

Planned contents:

- `.pre-commit-hooks.yaml` so other repositories can reference these hooks.
- An example `.pre-commit-config.yaml` for a consuming project.

Built on [pre-commit](https://github.com/pre-commit/pre-commit).

**Status:** Structure only; no hooks are published yet.
