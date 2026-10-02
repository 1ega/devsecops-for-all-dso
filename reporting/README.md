# Reporting

Source code and specifications for normalizing, deduplicating, and presenting security findings belong here.

| Path | Purpose |
| :--- | :--- |
| [severity-and-metadata.md](severity-and-metadata.md) | One severity scale across tools and the metadata every rule should carry |
| [compliance-mapping](compliance-mapping/README.md) | MASVS, ASVS 5.0, and Prowler compliance frameworks, plus mappings of rules and policies to them |

Future work may include SARIF/JSON adapters, review baselines, and local HTML reports. Importing findings into DefectDojo lives in [integrations/defectdojo](../integrations/defectdojo/README.md).

Keep generated reports and sensitive findings out of the repository. Any shared format should document severity, evidence, source tool, and stable finding identifiers.

**Status:** Draft conventions only; no reporting tools are published yet.
