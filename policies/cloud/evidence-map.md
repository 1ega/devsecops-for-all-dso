# Cloud baseline evidence map

Use this with [`baseline/controls.json`](../../baseline/controls.json). Collect
read-only evidence in each production account, project or subscription. Record
the account identifier, region or scope, review date, owner and a private link
in the assessment. A provider dashboard score is a lead for investigation, not
proof that every account is covered.

| Control | AWS | Google Cloud | Azure |
| --- | --- | --- | --- |
| `GOV-01`, `CLD-01` | Account inventory; CloudTrail trail and logging status | Organization/project inventory; Cloud Audit Logs configuration | Subscription inventory; Activity Log export and retention |
| `ID-02`, `CLD-02` | IAM users, roles and external access findings | IAM policies, service accounts and external principals | Role assignments, privileged identities and external users |
| `CLD-02`, `NET-01` | Public endpoints, security groups and load balancers | External IPs, firewall rules and load balancers | Public IPs, network security groups and exposed services |
| `CLD-03` | S3 public access settings and IAM Access Analyzer findings | Cloud Storage public access prevention and bucket IAM | Storage account anonymous blob access and role assignments |
| `BKP-01`, `BKP-02` | Backup plan, job status and a restore result | Backup policy/job status and a restore result | Backup policy/job status and a restore result |
| `LOG-02`, `VUL-01` | Alerts and findings with owner and ticket | Security Command Center findings with owner and ticket | Defender for Cloud findings with owner and ticket |

For every finding, record the affected asset from the inventory. Prioritize a
production asset exposed to the internet or containing sensitive data. Link the
remediation ticket and retest after the change. Collect exports through a
least-privilege read-only role; do not put credentials or raw logs in this repo.

Provider documentation:

- AWS: [IAM Access Analyzer for S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-analyzer.html)
- Google Cloud: [Cloud Audit Logs practices](https://docs.cloud.google.com/logging/docs/audit/best-practices) and [public access prevention](https://docs.cloud.google.com/storage/docs/public-access-prevention)
- Azure: [Activity Log](https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log), [Defender for Cloud inventory](https://learn.microsoft.com/en-us/azure/defender-for-cloud/asset-inventory), and [anonymous blob access](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-configure)
