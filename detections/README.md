# Detections

Detection content for security operations belongs here. Packs can be grouped by engine, such as `sigma/`, `yara/`, `falco/`, and `osquery/`.

A detection should include the rule, sample events or files, expected matches and non-matches, tuning notes, and its source and license. Keep environment-specific values out of shared rules.

| Directory | Contents |
| :--- | :--- |
| [yara](yara/README.md) | Five imported YARA rule sets (signature-base, ReversingLabs, bartblaze, Elastic, Yara-Rules community), about 2,700 rule files |
| [falco](falco/README.md) | Runtime detection deployment examples and an alert triage runbook |

**Status:** Imported YARA rule sets in `yara/`; Falco has deployment guidance and existing example rules. A validated detection pack with sample events and tuning tests remains planned.
