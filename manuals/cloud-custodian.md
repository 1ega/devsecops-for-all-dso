# Cloud Custodian

**Area:** 8. Secure the cloud → Cloud posture (CSPM)  
**License:** Apache-2.0

[GitHub: cloud-custodian/cloud-custodian](https://github.com/cloud-custodian/cloud-custodian) · [Documentation](https://cloudcustodian.io/docs/)

## What it is for

YAML policies that find and optionally fix non-compliant cloud resources.

Goes beyond reporting: the same policy can tag, notify, stop, or delete offending resources, and it runs on a schedule or on cloud events.

## Install

**pip (add c7n-azure or c7n-gcp for other clouds)**

```bash
pip install c7n
```

## Use

**Example policy (policy.yml)**

```yaml
policies:
  - name: ec2-without-owner
    resource: aws.ec2
    filters:
      - "tag:Owner": absent
```

**Validate, dry-run, then run**

```bash
custodian validate policy.yml
custodian run --dryrun -s out policy.yml
custodian run -s out policy.yml
```

## Output and triage

Matched resources are written under the output directory. Always start with `--dryrun` before adding actions.

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
- [Steampipe and Powerpipe](steampipe.md) — Query cloud APIs with SQL and run compliance benchmarks with dashboards.
- [CloudSploit](cloudsploit.md) — Configuration checks for AWS, Azure, GCP, and Oracle Cloud with compliance filters.
