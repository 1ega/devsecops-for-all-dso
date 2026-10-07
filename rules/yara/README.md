# YARA rules

Open-source YARA rule sets, imported unchanged, one directory per upstream project. Use them to scan files, build artifacts, container image layers, and incident samples for known malware, hack tools, webshells, and suspicious file traits. Each directory has the upstream license and a `SOURCE.md` with the exact commit, what was left out, and known compile issues.

| Directory | Covers | Rule files | Rules (about) | License |
| :--- | :--- | ---: | ---: | :--- |
| [signature-base](signature-base/SOURCE.md) | APT and crimeware, hack tools, webshells, exploits, file anomalies (Florian Roth, Nextron Systems) | 751 | 5,950 | DRL 1.1 |
| [reversinglabs](reversinglabs/SOURCE.md) | Windows and Linux malware families, certificates; tuned for low false positives | 310 | 1,240 | MIT |
| [bartblaze](bartblaze/SOURCE.md) | APT, crimeware, ransomware, hack tools, generic file traits | 110 | 140 | MIT |
| [elastic](elastic/SOURCE.md) | Elastic Defend malware protection rules for Windows, Linux, macOS | 1,056 | 3,070 | Elastic License 2.0 |
| [yara-rules-community](yara-rules-community/SOURCE.md) | Older community collection: malware, maldocs, webshells, CVEs, packers, crypto, anti-VM; not updated since 2022 | 500 | 12,800 | GPL-2.0 |

About 9,300 of the community rules are PEiD-style packer signatures. Rule sets overlap: 119 files have rule names that also appear in another set, so load each set into its own namespace when you combine them.

## Running the rules

With [YARA-X](https://github.com/VirusTotal/yara-x) (`yr`), pass a rules directory or file, then the target:

```sh
yr scan --recursive rules/yara/reversinglabs/yara path/to/target
yr scan --recursive rl:rules/yara/reversinglabs/yara bb:rules/yara/bartblaze/rules path/to/target
```

The `name:` prefix puts each set in its own namespace. Add `--relaxed-re-syntax` for `yara-rules-community`, which has a few regular expressions that only classic YARA accepts.

The four sets that compile cleanly together, with the `signature-base` external variables defined as empty strings (see below):

```sh
yr scan --recursive --disable-warnings \
  --define filename='""' --define filepath='""' --define extension='""' --define filetype='""' --define owner='""' \
  sb:rules/yara/signature-base rl:rules/yara/reversinglabs bb:rules/yara/bartblaze el:rules/yara/elastic \
  path/to/target
```

With classic [YARA](https://github.com/VirusTotal/yara), pass one or more rule files; `-r` scans a target directory recursively:

```sh
yara -r rules/yara/bartblaze/rules/crimeware/AveMaria.yar path/to/target
yara -r rules/yara/yara-rules-community/malware_index.yar path/to/target
```

The `*_index.yar` files in `yara-rules-community/` include a whole category at once. To scan with many files, compile them first with `yarac` or use `yr`.

## External variables

Thirteen `signature-base` files use the external variables `filename`, `filepath`, `extension`, `filetype`, and `owner`, which THOR and LOKI set per file. Other engines fail with `undefined identifier` unless you define them (`yara -d filename=x ...`, `yr scan --define filename=x ...`), and then those conditions test your dummy values. The file list is in [signature-base/SOURCE.md](signature-base/SOURCE.md); leave those files out of a plain scan. Some `yara-rules-community` rules need modules that not every build has, such as `cuckoo`.

## False positives

These rules are written for binaries, documents, and memory, not for source trees.

- Scanning source code, a dependency cache, or a security tool's own repository produces many hits, because webshell, hack-tool, and exploit rules match the strings that defensive code, test fixtures, and documentation contain. Exclude rule repositories (including this directory), AV signature files, and test samples from the target.
- Generic and informational rules (for example bartblaze `rules/generic/` with `category = "INFO"`, packer and crypto-constant rules) describe file traits, not malware. Report them separately from malware matches.
- For CI, prefer the precise sets (`reversinglabs`, `elastic`, malware-specific `signature-base` files) on build outputs and images, start in report-only mode, and record every suppression with a reason.
- Check a rule's `score`, `description`, and `reference` metadata before acting on a match.

## Licenses

Each directory keeps its upstream license. Points to note:

- **DRL 1.1** (`signature-base`): keep the rule `author`, a link to the rule set, and the license reference when sharing rules or match reports.
- **Elastic License 2.0** (`elastic`): source-available, not OSI open source. Use and redistribution are allowed with the license attached; offering the rules to others as a hosted or managed service is not.
- **GPL-2.0** (`yara-rules-community`): changes that you distribute must stay under GPL-2.0.
- Some `signature-base` and `yara-rules-community` files carry a CC BY-NC or CC BY-NC-SA 4.0 (non-commercial) statement on individual rules. They are listed in each `SOURCE.md`; review them before commercial use.

See [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

## Compile check

Every file was compiled on its own with YARA 4.5.4 (yara-python) and YARA-X 1.21.0. All files in `signature-base`, `reversinglabs`, `bartblaze`, and `elastic` compile; the 13 `signature-base` files that use external variables need them defined. In `yara-rules-community`, 7 files compile only together with `malware/000_common_rules.yar`, 1 needs the `cuckoo` module, and 4 fail in YARA-X (2 of them compile with `--relaxed-re-syntax`); details are in its `SOURCE.md`.

## Related

- [Trail of Bits `yara-authoring` skill](../../skills/trailofbits/yara-authoring/) for writing and testing your own rules.
- [YARA Forge](https://github.com/YARAHQ/yara-forge) publishes curated, deduplicated, and quality-tested packages built from many public rule sets (core, extended, full). Download a release instead of vendoring when you want broad coverage with less tuning.
- [InQuest/awesome-yara](https://github.com/InQuest/awesome-yara) is a curated list of further rule sets, tools, and articles.

**Status:** Five upstream rule sets imported unchanged (about 2,700 rule files); no tuned profiles, fixtures, or CI integration of our own yet.
