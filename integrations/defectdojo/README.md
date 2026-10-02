# DefectDojo

Sends scan results to [DefectDojo](https://github.com/DefectDojo/django-DefectDojo) so findings from every tool are tracked, deduplicated, and closed in one place.

Planned contents:

- A script or CI job that calls `import-scan` / `reimport-scan` through API v2.
- Mapping conventions: repository → product, branch or pipeline → engagement, tool → test type.
- Deduplication and auto-close settings for fixed findings.
- Severity mapping from [`reporting/severity-and-metadata.md`](../../reporting/severity-and-metadata.md).

Keep the API token in CI secrets; never commit it or print it in job logs.

Open questions:

- Which DefectDojo parser to use per tool (generic SARIF or the tool's native parser).
- Whether a product maps to a team or to a service.

**Status:** Structure only; no integration is published yet.
