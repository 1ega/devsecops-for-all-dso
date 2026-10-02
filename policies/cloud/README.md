# Cloud

Checks for deployed cloud accounts: IAM, networking, encryption, and logging. They complement [terraform](../terraform/README.md): IaC policies catch problems before deploy, cloud checks catch what is already running, including manual changes.

| Directory | Provider |
| :--- | :--- |
| [aws](aws/README.md) | Amazon Web Services |
| [gcp](gcp/README.md) | Google Cloud |
| [azure](azure/README.md) | Microsoft Azure |

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| Prowler | [prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | AWS, GCP, Azure, Kubernetes; CIS and PCI DSS frameworks |
| ScoutSuite | [nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) | Multi-cloud audit |
| Cloud Custodian | [cloud-custodian/cloud-custodian](https://github.com/cloud-custodian/cloud-custodian) | Policies with optional remediation |
| Steampipe | [turbot/steampipe](https://github.com/turbot/steampipe) | SQL queries over cloud APIs |
| PMapper | [nccgroup/PMapper](https://github.com/nccgroup/PMapper) | AWS IAM privilege escalation paths |

Scanners should run with dedicated read-only roles. Document the exact permissions each check needs.

**Status:** Structure only; no policies are published yet.
