# Secret rules

Rule sets for finding credentials in source code, configuration and mobile builds.

| Package | Use |
| :--- | :--- |
| [gitleaks-default](gitleaks-default/SOURCE.md) | The upstream Gitleaks default configuration, unchanged. A base for `[extend]` configs. |
| [apkleaks](apkleaks/SOURCE.md) | APKLeaks patterns for URIs, endpoints and secrets in built APKs. |
| [secrets-patterns-db](secrets-patterns-db/SOURCE.md) | A large regex database (CC-BY-SA-4.0) to draw extra rules from. Review each pattern before using it. |

## Run

Install [Gitleaks](../../manuals/gitleaks.md) and run from the repository root. Scan a working tree:

```bash
gitleaks dir --no-banner --redact --config rules/secrets/gitleaks-default/gitleaks.toml \
  --report-format json --report-path /private/reports/gitleaks.json path/to/project
```

Scan the full Git history, where removed secrets still live until they are rotated:

```bash
gitleaks git --no-banner --redact --config rules/secrets/gitleaks-default/gitleaks.toml \
  --report-format json --report-path /private/reports/gitleaks-history.json path/to/repository
```

Exit code 1 means findings. The config ignores files named `gitleaks.toml` and
honours `.gitleaksignore` and inline `gitleaks:allow` comments in the target, so a
target can hide its own secrets. Add `--ignore-gitleaks-allow` when the target is
not trusted. `--redact` keeps secret values out of the report; treat the report as
confidential anyway, because it still points at every secret.

A secret found in history must be rotated even if the latest commit removed it.
Follow the [leaked secret playbook](../../playbooks/leaked-secret.md).
