# YARA-Rules community rules

The community YARA rule collection from the Yara-Rules project: malware, APT, webshells, malicious documents, exploit kits, CVEs, packers, crypto constants, anti-debug and anti-VM techniques, and e-mail rules. The project has not been updated since 2022.

| | |
| :--- | :--- |
| Upstream | [Yara-Rules/rules](https://github.com/Yara-Rules/rules) |
| Commit | [`0f93570194a8`](https://github.com/Yara-Rules/rules/tree/0f93570194a80d2f2032869055808b0ddcdfb360) (2022-04-12) |
| License | GPL-2.0 — see the license file in this directory |
| Included | `antidebug_antivm/`, `capabilities/`, `crypto/`, `cve_rules/`, `email/`, `exploit_kits/`, `maldocs/`, `malware/`, `packers/`, `utils/`, `webshells/`, the `*index*.yar` files, `README.md`, `LICENSE` — 500 rule files (487 rule files and 13 index files), about 12,800 rules |

## Changes

Files were copied without changes except:

- `deprecated/` was not copied (upstream marks it deprecated; its mobile rules need the abandoned Androguard module). No included index file references it.
- `index_gen.sh`, `.gitmodules`, `.travis.yml`, `.github/`, `mobile_malware/.gitKeep`, `utils/README`, the sample e-mails in `email/eml/`, and `malware/Operation_Blockbuster/mastersig` (no `.yar` extension) were not copied.
- The executable bit was removed from `malware/APT_furtim.yar`, `malware/APT_fancybear_dnc.yar`, and `malware/APT_Stuxnet.yar`. File contents are unchanged.
- Cyrillic check: 0 files contained Cyrillic characters, so no files were excluded.

To update, replace this directory with the same paths from a newer upstream commit and update this file.

## Rule counts

About 7,600 of the rules are PEiD packer signatures in `packers/peid.yar` and about 1,660 are in `packers/packer.yar`; the remaining files hold about 3,500 rules. Many older malware and webshell rules here also appear, often in newer form, in `../signature-base/`.

## Licensing notes

The collection is GPL-2.0. A few files carry other statements, left as they are: `malware/MALW_Cloaking.yar` and `malware/TOOLKIT_THOR_HackTools.yar` state CC BY-NC-SA 4.0 (non-commercial); some ESET rules state BSD 2-Clause and `malware/MALW_Monero_Miner_installer.yar` states MIT.

## Known issues

Per-file compile check with YARA 4.5.4 (yara-python) and YARA-X 1.21.0:

- 7 files use the private rule `is__elf` from `malware/000_common_rules.yar` and do not compile on their own: `MALW_Httpsd_ELF.yar`, `MALW_Mirai_Okiru_ELF.yar`, `MALW_Mirai_Satori_ELF.yar`, `MALW_Rebirth_Vulcan_ELF.yar`, `MALW_TinyShell_Backdoor_gen.yar`, `MALW_Torte_ELF.yar`, `TOOLKIT_Mandibule.yar` (all in `malware/`). They compile through `malware_index.yar` or when the whole directory is loaded.
- `malware/MALW_AZORULT.yar` uses the `cuckoo` module. It fails in YARA builds without that module (including the yara-python wheel) and compiles in YARA-X.
- YARA-X only: `malware/APT_CrashOverride.yar` (`pe.exports(...) & pe.characteristics` is a type error) and `malware/RAT_PoetRATPython.yar` (a regular expression that can match an empty string) fail; `malware/RAT_PlugX.yar` and `webshells/Wshell_ChineseSpam.yar` compile only with `--relaxed-re-syntax`. All four compile with classic YARA.
- Because of the above, `index.yar`, `index_w_mobile.yar`, and `malware_index.yar` fail in YARA-X, and in classic YARA builds without `cuckoo`; `webshells_index.yar` fails in YARA-X without `--relaxed-re-syntax`.

Loaded as one rule set in YARA-X (all files except the index files), 485 of 487 files compile with `--relaxed-re-syntax`; skip `APT_CrashOverride.yar` and `RAT_PoetRATPython.yar`.
