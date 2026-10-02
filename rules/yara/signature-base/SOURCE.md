# Neo23x0 signature-base YARA rules

YARA rules by Florian Roth (Nextron Systems) and contributors for APT and crimeware malware, hack tools, webshells, exploits, and suspicious file anomalies.

| | |
| :--- | :--- |
| Upstream | [Neo23x0/signature-base](https://github.com/Neo23x0/signature-base) |
| Commit | [`94a1c48d7ab4`](https://github.com/Neo23x0/signature-base/tree/94a1c48d7ab499879287ff611dfe7f9c56376030) (2026-09-08) |
| License | Detection Rule License (DRL) 1.1 — see the license file in this directory |
| Included | `yara/`, `README.md`, `LICENSE` — 751 rule files, about 5,950 rules |

## Changes

Files were copied without changes except:

- Only `.yar` and `.yara` files from `yara/` were copied. `iocs/`, `misc/`, `scripts/`, `tests/`, `vendor/`, `build-rules.py`, `makefile`, `sig-base-rules.csv`, `_config.yml`, `Code_of_Conduct.md`, and repository metadata (`.git`, `.github`, CI and ignore files) were not copied.
- `yara/external-variable-rules.txt` was not copied; its list of files is reproduced below.
- The executable bit was removed from `yara/apt_terracotta_liudoor.yar`. File contents are unchanged.
- Cyrillic check: 0 files contained Cyrillic characters, so no files were excluded.

To update, replace this directory with the same paths from a newer upstream commit and update this file.

## External variables

These 13 files use the external variables `filename`, `filepath`, `extension`, `filetype`, and `owner`. They are written for [THOR](https://www.nextron-systems.com/thor/) and [LOKI](https://github.com/Neo23x0/Loki), which set those values per scanned file. Other engines report `undefined identifier` unless you define them, for example `yara -d filename=x -d filepath=x -d extension=x -d filetype=x -d owner=x` or `yr scan --define filename=x ...`, in which case the conditions that use them evaluate against your dummy values. Leave these files out of a plain scan if you do not need them.

`generic_anomalies.yar`, `general_cloaking.yar`, `gen_webshells_ext_vars.yar`, `thor_inverse_matches.yar`, `yara_mixed_ext_vars.yar`, `configured_vulns_ext_vars.yar`, `gen_fake_amsi_dll.yar`, `expl_citrix_netscaler_adc_exploitation_cve_2023_3519.yar`, `expl_connectwise_screenconnect_vuln_feb24.yar`, `gen_mal_3cx_compromise_mar23.yar`, `gen_susp_obfuscation.yar`, `gen_vcruntime140_dll_sideloading.yar`, `yara-rules_vuln_drivers_strict_renamed.yar`

## Licensing notes

The repository is under DRL 1.1, which requires keeping the rule `author` field, a link to the rule set, and a reference to the license when sharing rules or reporting matches. The upstream README notes that the repository moved from CC BY-NC to DRL 1.1 in August 2021, and some files still carry other license statements in a file header or a rule's `license` field. They were left as they are:

- CC BY-NC 4.0 or CC BY-NC-SA 4.0 (non-commercial): `apt_apt27_hyperbro.yar`, `apt_apt41.yar`, `apt_exile_rat.yar`, `crime_malware_generic.yar`, `crime_nansh0u.yar`, `crime_xbash.yar`, `gen_excel_auto_open_evasion.yar`, `gen_excel_xll_addin_suspicious.yar`, `gen_excel_xor_obfuscation_velvetsweatshop.yar`, `gen_github_net_redteam_tools_names.yar`, `generic_anomalies.yar`, `hktl_HvS_nfs_security_tooling.yar`, `thor-hacktools.yar` (in several of these, only one or a few rules carry the non-commercial license). Review these before commercial use.
- Other permissive licenses on individual rules: BSD 2-Clause (ESET and Volexity rules), MIT, CC BY 4.0, Apache-2.0 (Google GCTI Cobalt Strike and Sliver rules), the UK Open Government Licence v3.0, the CAPEv2 license, and the FireEye SUNBURST countermeasures license.

## Known issues

All 751 files compile with YARA 4.5.4 (yara-python) and YARA-X 1.21.0. The 13 files above compile only when the external variables are defined. With the external variables defined, the whole `yara/` directory also compiles as one rule set in YARA-X, with no duplicate rule names.
