# Steampipe and Powerpipe

**Area:** 8. Secure the cloud → Cloud posture (CSPM)  
**License:** AGPL-3.0

[GitHub: turbot/steampipe](https://github.com/turbot/steampipe) · [Documentation](https://steampipe.io/docs)

## What it is for

Query cloud APIs with SQL and run compliance benchmarks with dashboards.

Ask ad-hoc questions ("which buckets are public?") in SQL, and run ready CIS, PCI, and NIST benchmarks for AWS, Azure, and Google Cloud.

## Install

**Homebrew**

```bash
brew install turbot/tap/steampipe turbot/tap/powerpipe
steampipe plugin install aws
```

## Use

**Run the AWS CIS benchmark**

```bash
powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance
steampipe service start
powerpipe benchmark run aws_compliance.benchmark.cis_v400
```

## Output and triage

Benchmarks print pass, fail, and skip per control; `powerpipe server` opens the dashboards in a browser.

## Concepts to know

- IAM and least privilege
- Cloud activity logs
- Landing zone and organization policy
- Network segmentation
- Encryption by default
- Public exposure

## Related tools

- [Prowler](prowler.md) — Hundreds of checks for AWS, Azure, GCP, and Kubernetes, mapped to CIS, PCI DSS, ISO 27001, and more.
- [ScoutSuite](scoutsuite.md) — Multi-cloud audit that builds an offline HTML report of risky configuration.
- [Cloud Custodian](cloud-custodian.md) — YAML policies that find and optionally fix non-compliant cloud resources.
- [CloudSploit](cloudsploit.md) — Configuration checks for AWS, Azure, GCP, and Oracle Cloud with compliance filters.
