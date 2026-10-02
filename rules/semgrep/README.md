# Semgrep rule packs

Keep substantial rule collections in one directory per pack, with their own usage, tests, provenance, and license information.

| Pack | Coverage |
| :--- | :--- |
| [mobile_custom](mobile/README.md) | Android, iOS, React Native, and Flutter — 320 rules |
| [elttam](elttam/SOURCE.md) | Java, Go, PHP, YAML, and generic rules from elttam — 109 rules, MIT |
| [trailofbits](trailofbits/SOURCE.md) | Go, Python, JavaScript, JVM, Rust, Ruby, HCL, and more from Trail of Bits — 124 rules, AGPL-3.0 |
| [profiles](profiles/README.md) | Planned rule selections: `ci-blocking`, `pr-diff`, `audit` |

Known issue: on Semgrep 1.175.0, 12 Java rules in `elttam/` fail to parse (for example `jax-rs.path-class` and `rest-RequestMapping`), and `semgrep --validate` also reports `rules/generic/jsp-likely-xss.yaml`, which is a test file next to its rule. Exclude those rules with `--exclude-rule` until they are fixed; `trailofbits/` validates cleanly (120 rules).

Run an imported pack the same way as the mobile one, for example `semgrep scan --metrics=off --config rules/semgrep/trailofbits/ path/to/project`. Imported packs keep their upstream license; see each `SOURCE.md` and [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

The smaller [Python starter rules](python/README.md) predate this layout and remain available in `rules/`. Future packs, such as backend rules for other languages, can be added here without changing existing paths.
