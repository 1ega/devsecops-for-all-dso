# ReversingLabs YARA rules

Precision-focused YARA rules from ReversingLabs for Windows and Linux malware families: backdoors, downloaders, exploits, infostealers, PUA, ransomware, rootkits, trojans, viruses, and malicious certificates.

| | |
| :--- | :--- |
| Upstream | [reversinglabs/reversinglabs-yara-rules](https://github.com/reversinglabs/reversinglabs-yara-rules) |
| Commit | [`e0a0be54aa1e`](https://github.com/reversinglabs/reversinglabs-yara-rules/tree/e0a0be54aa1e11ccfd6854e4f19e9476f328fd84) (2025-11-03) |
| License | MIT — see the license file in this directory |
| Included | `yara/`, `README.md`, `LICENSE` — 310 rule files, about 1,240 rules |

## Changes

Files were copied without changes except:

- Repository metadata (`.git`) was not copied. The upstream repository contains no other files.
- Cyrillic check: 0 files contained Cyrillic characters, so no files were excluded.

To update, replace this directory with the same paths from a newer upstream commit and update this file.

## Known issues

All 310 files compile with YARA 4.5.4 (yara-python) and YARA-X 1.21.0. The rules use the `pe` and `elf` modules.
