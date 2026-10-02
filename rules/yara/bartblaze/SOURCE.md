# bartblaze YARA rules

YARA rules by Bart Parys for APT and crimeware families, ransomware, hack tools, and generic file traits such as packers and script wrappers.

| | |
| :--- | :--- |
| Upstream | [bartblaze/Yara-rules](https://github.com/bartblaze/Yara-rules) |
| Commit | [`5cc871d82361`](https://github.com/bartblaze/Yara-rules/tree/5cc871d82361de8a80d387ec8bbd01fe4258b4a9) (2026-01-28) |
| License | MIT — see the license file in this directory |
| Included | `rules/`, `README.md`, `LICENSE` — 110 rule files, about 140 rules |

## Changes

Files were copied without changes except:

- Repository metadata (`.git`, `.github`) and `CONTRIBUTING.md` were not copied.
- `rules/crimeware/GootLoader_Dotnet` was not copied because it has no `.yar` extension. It is a single rule; take it from upstream if needed.
- Cyrillic check: 0 files contained Cyrillic characters, so no files were excluded.

To update, replace this directory with the same paths from a newer upstream commit and update this file.

## Known issues

All 110 files compile with YARA 4.5.4 (yara-python) and YARA-X 1.21.0. Rules in `rules/generic/` with `category = "INFO"` describe file traits (for example AutoIt or a packer) and are not malware verdicts.
