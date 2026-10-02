# Semgrep rule packs

Keep substantial rule collections in one directory per pack, with their own usage, tests, provenance, and license information.

| Pack | Coverage |
| :--- | :--- |
| [mobile_custom](mobile_custom/README.md) | Android, iOS, React Native, and Flutter — 320 rules |
| [profiles](profiles/README.md) | Planned rule selections: `ci-blocking`, `pr-diff`, `audit` |

The smaller [Python starter rules](../rules/README.md) predate this layout and remain available in `rules/`. Future packs, such as backend rules for other languages, can be added here without changing existing paths.
