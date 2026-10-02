# Local secret check

Copy [.pre-commit-config.yaml](.pre-commit-config.yaml) to the application's root.
Install a reviewed `pre-commit` package, then run:

```bash
pre-commit install
pre-commit run --all-files
```

The hook is Gitleaks v8.30.1. Initial setup downloads its environment; pin and
review hook upgrades. A hook can be bypassed, so keep CI secret checks enabled.
Run a full-history scan before adoption and rotate exposed credentials. Scope
fixture exceptions to known dummy values; do not suppress every test directory.
See [Gitleaks](../../manuals/gitleaks.md) and [leak response](../../playbooks/leaked-secret.md).
