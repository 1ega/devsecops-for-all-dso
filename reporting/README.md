# Reporting

Source code and specifications for normalizing, deduplicating, and presenting security findings belong here.

| Path | Purpose |
| :--- | :--- |
| [severity-and-metadata.md](severity-and-metadata.md) | One severity scale across tools and the metadata every rule should carry |
| [compliance-mapping](compliance-mapping/README.md) | MASVS, ASVS 5.0, and Prowler compliance frameworks, plus mappings of rules and policies to them |

The [DSO report contract](dso-report.md) and [CLI](../tools/dso/README.md) provide Gitleaks/Semgrep/Trivy JSON adapters, within-tool deduplication and review-baseline gates. HTML reports and further adapters remain future work. Importing findings into DefectDojo lives in [integrations/defectdojo](../integrations/defectdojo/README.md).

Keep generated reports and sensitive findings out of the repository. Any shared format should document severity, evidence, source tool, and stable finding identifiers.

**Status:** DSO scan normalization and gates implemented; operational lifecycle conventions remain templates.

Original templates: [finding record](finding.example.json), [finding lifecycle](finding-lifecycle.md) and [exceptions](exceptions.example.json). Owner/SLA enrichment and DefectDojo ingestion remain planned.
