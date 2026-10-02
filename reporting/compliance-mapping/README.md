# Compliance mapping

Tables that map rules and policies to standard requirements, to show coverage during an audit and to find gaps. They are generated from rule metadata (`cwe`, `masvs`, `owasp`), so they depend on the conventions in [severity-and-metadata.md](../severity-and-metadata.md).

| Standard | Area | Source |
| :--- | :--- | :--- |
| OWASP MASVS / MASTG | Mobile | [OWASP/masvs](https://github.com/OWASP/masvs), [OWASP/mastg](https://github.com/OWASP/mastg) |
| OWASP ASVS | Web and API | [OWASP/ASVS](https://github.com/OWASP/ASVS) |
| OWASP Top 10 / API Security Top 10 | Web and API | [owasp.org](https://owasp.org/) |
| PCI DSS 4.0 | Payment data | [PCI Security Standards Council](https://www.pcisecuritystandards.org/) |
| CIS Benchmarks | Cloud, Kubernetes, containers, hosts | [CIS](https://www.cisecurity.org/cis-benchmarks) |

Imported standards and mappings:

| Directory | Contents | License |
| :--- | :--- | :--- |
| [masvs](masvs/SOURCE.md) | OWASP MASVS controls | CC-BY-SA-4.0 |
| [asvs-5.0](asvs-5.0/SOURCE.md) | OWASP ASVS 5.0 chapters, requirements as CSV and JSON, and mappings to 4.0.3 and CWE | CC-BY-SA-4.0 |
| [prowler](prowler/SOURCE.md) | Prowler requirement-to-check mappings for AWS, Azure, GCP, Kubernetes, and GitHub: CIS, PCI DSS 3.2.1 and 4.0, ISO 27001, SOC 2, NIST, HIPAA, GDPR, and more | Apache-2.0 |

The Prowler files give a ready mapping from PCI DSS 4.0 requirements to automated cloud checks (for example [prowler/aws/pci_4.0_aws.json](prowler/aws/pci_4.0_aws.json)). A rule → PCI DSS mapping for code-level rules still has to be built from rule metadata.

Related skill: [compliance](../../skills/compliance/compliance/SKILL.md).

**Status:** Standards and cloud mappings imported; mappings for this repository's rules are not published yet.
