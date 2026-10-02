# Elastic Security YARA rules

YARA rules that Elastic Defend uses for malware protection on Windows, Linux, and macOS: trojans, ransomware, cryptominers, attack frameworks, hack tools, and more.

| | |
| :--- | :--- |
| Upstream | [elastic/protections-artifacts](https://github.com/elastic/protections-artifacts) |
| Commit | [`90c1d57c9c22`](https://github.com/elastic/protections-artifacts/tree/90c1d57c9c2b2240f65b40653f298f70ce783d29) (2026-10-01) |
| License | Elastic License 2.0 — see the license file in this directory |
| Included | `yara/rules/`, `yara/README.md`, `README.md`, `LICENSE.txt` — 1,056 rule files, about 3,070 rules |

## Changes

Files were copied without changes except:

- Only the YARA rules were copied. `behavior/` (EQL rules), `ransomware/`, `SDP.md`, `yara/CONTRIBUTING.md`, and repository metadata (`.git`, `.github`, ignore and attribute files) were not copied.
- Cyrillic check: 0 files contained Cyrillic characters, so no files were excluded.

To update, replace this directory with the same paths from a newer upstream commit and update this file.

## Licensing notes

The Elastic License 2.0 (ELv2) is source-available, not an OSI open-source license. It allows using, copying, distributing, and modifying the rules, provided that:

- anyone who receives a copy also receives the license terms (the license file in this directory);
- licensing and copyright notices are not removed, including the `license = "Elastic License v2"` field in each rule;
- modified copies carry a prominent notice that they were changed;
- the rules are not provided to third parties as a hosted or managed service that gives access to a substantial set of their functionality.

Using them for your own scanning, hunting, or CI checks is within those terms. Offering them as part of a scanning service for other organizations is not.

## Known issues

All 1,056 files compile with YARA 4.5.4 (yara-python) and YARA-X 1.21.0. The rules use no modules and are designed for Elastic Endpoint, so some may be noisier on other data.
