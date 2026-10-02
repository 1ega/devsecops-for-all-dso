# ScoutSuite

**Area:** 8. Secure the cloud → Cloud posture (CSPM)  
**License:** GPL-2.0

[GitHub: nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) · [Documentation](https://github.com/nccgroup/ScoutSuite/wiki)

## What it is for

Multi-cloud audit that builds an offline HTML report of risky configuration.

Built by security consultants for point-in-time reviews: one run collects the configuration, and the report can then be explored offline.

## Install

**pip in a virtual environment**

```bash
python3 -m venv venv && . venv/bin/activate
pip install scoutsuite
scout --help
```

## Use

**Audit an AWS account with a named profile**

```bash
scout aws --profile my-audit-profile
```

## Output and triage

Opens an HTML report with findings per service. Use a read-only audit role.

## Concepts to know

- IAM and least privilege
- Cloud activity logs
- Landing zone and organization policy
- Network segmentation
- Encryption by default
- Public exposure

## Related tools

- [Prowler](prowler.md) — Hundreds of checks for AWS, Azure, GCP, and Kubernetes, mapped to CIS, PCI DSS, ISO 27001, and more.
- [Cloud Custodian](cloud-custodian.md) — YAML policies that find and optionally fix non-compliant cloud resources.
- [Steampipe and Powerpipe](steampipe.md) — Query cloud APIs with SQL and run compliance benchmarks with dashboards.
- [CloudSploit](cloudsploit.md) — Configuration checks for AWS, Azure, GCP, and Oracle Cloud with compliance filters.
