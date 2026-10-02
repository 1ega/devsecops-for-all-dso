# Finding ownership, deadlines and verification

Use [finding.example.json](finding.example.json) as a private record. Required
operational fields: stable finding/rule/tool/asset identifiers, environment,
native plus normalized severity where available, confidence, owner, status,
first detection, due date, evidence, deployed version/digest and remediation
ticket. Include exposure, data criticality, known exploitation and fix availability.
The example is a lifecycle format guide. [DSO scan adapters](dso-report.md) normalize scanner output and deduplicate within each tool; automatic lifecycle enrichment and external ingestion remain unimplemented.

Suggested starter deadlines below are company policy choices, not regulatory
deadlines. Adopt them with the service owners and measure overdue findings.

| Situation | Initial response | Remediation decision |
| :--- | :--- | :--- |
| Active compromise or leaked privileged secret | Incident response immediately | Contain/revoke, investigate scope, verify recovery |
| Confirmed exploited/exposed critical weakness | Same working day | Mitigate immediately; owner sets a dated fix plan |
| Confirmed high-impact production vulnerability | One working day | Target seven days or an approved shorter/exception date |
| Context-dependent medium / hardening | Weekly triage | Target 30 / 90 days based on exposure and business risk |

States: `open → triaged → remediation → verified → closed`; `false_positive`
needs evidence; `accepted_risk` needs a separate expiring approved exception.
Prioritize production exposure/KEV/data reachability, not CVSS alone. A clean
new report closes a finding only if the same asset, scope, version and check
were actually covered. Missing scans, permission errors and incomplete imports
must not silently close findings. Reimport settings need deliberate review.

Retest the deployed system, preserve the result, and reopen recurring findings.
See [triage](../playbooks/vulnerability-triage.md),
[exceptions](exceptions.example.json) and [DefectDojo](../manuals/defectdojo.md).
