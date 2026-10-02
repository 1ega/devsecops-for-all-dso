# Rules

Every rule set in the repository, grouped by the engine that runs it. Scanner wrappers and configuration live in [`scanners/`](../scanners/README.md); policy-as-code for Kubernetes, CI/CD, and infrastructure lives in [`policies/`](../policies/README.md).

| Directory | Engine | Contents | Status |
| :--- | :--- | :--- | :--- |
| [semgrep/python](semgrep/python/README.md) | Semgrep | 3 Python starter rules with tests | ✅ |
| [semgrep/mobile](semgrep/mobile/README.md) | Semgrep | 320 rules for Android, iOS, React Native / Expo, and Flutter / Dart | ✅ |
| [semgrep/trailofbits](semgrep/trailofbits/SOURCE.md) | Semgrep | 120 rules from Trail of Bits audits (AGPL-3.0) | 📦 |
| [semgrep/elttam](semgrep/elttam/SOURCE.md) | Semgrep | 107 rules for Java, Go, PHP, YAML, and generic code (MIT) | 📦 |
| [semgrep/profiles](semgrep/profiles/README.md) | Semgrep | Rule selections for CI gates, pull request comments, and audits | 🗺️ |
| [yara](yara/README.md) | YARA / YARA-X | Five malware rule sets, about 2,700 rule files: signature-base, Elastic, ReversingLabs, bartblaze, Yara-Rules community | 📦 |
| [secrets/gitleaks-default](secrets/gitleaks-default/SOURCE.md) | gitleaks | Upstream default `gitleaks.toml` (MIT) | 📦 |
| [secrets/secrets-patterns-db](secrets/secrets-patterns-db/SOURCE.md) | regex | Open database of secret patterns (CC-BY-SA-4.0) | 📦 |
| [secrets/apkleaks](secrets/apkleaks/SOURCE.md) | apkleaks | Secret and endpoint patterns for APKs (Apache-2.0) | 📦 |
| [nuclei](nuclei/fuzzing-templates/SOURCE.md) | nuclei | 21 fuzzing templates (MIT) | 📦 |
| [falco](falco/README.md) | Falco | Deployment guidance and an alert triage runbook | ✅ |
| `sigma/` | Sigma | Log detection rules | 🗺️ |

✅ our own content · 📦 imported with its license and `SOURCE.md` · 🗺️ planned.

## Run

```bash
# Semgrep: one pack, or several at once
semgrep scan --metrics=off --config rules/semgrep/mobile/rules/ path/to/app
semgrep scan --metrics=off --config rules/semgrep/trailofbits/ --config rules/semgrep/elttam/rules/ path/to/project

# YARA: one rule file against a directory
yara -r rules/yara/bartblaze/rules/crimeware/AveMaria.yar path/to/files

# gitleaks with the upstream default rules
gitleaks dir --config rules/secrets/gitleaks-default/gitleaks.toml path/to/project
```

A rule of our own should include the rule, matching and non-matching examples, tuning notes, and its source and license. Keep environment-specific values out of shared rules.
