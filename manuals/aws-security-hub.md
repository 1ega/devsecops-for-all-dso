# AWS Security Hub and GuardDuty

**Area:** 8. Secure the cloud → Native cloud security services  
**License:** AWS service (paid)  
**Recommended first choice in this topic.**

[Documentation](https://docs.aws.amazon.com/securityhub/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/reporting/compliance-mapping/prowler)

## What it is for

Security Hub aggregates findings and runs standards; GuardDuty detects threats from logs.

Covers what open-source scanners cannot: detection of active threats from CloudTrail, VPC flow, and DNS logs, across every account in the organization.

## Install

**Enable in an account (repeat per region, or use a delegated admin)**

```bash
aws securityhub enable-security-hub --enable-default-standards
aws guardduty create-detector --enable
```

## Use

**List high-severity findings**

```bash
aws securityhub get-findings --filters '{"SeverityLabel":[{"Value":"HIGH","Comparison":"EQUALS"}]}'
```

## Output and triage

Prowler can send its findings to Security Hub, so open-source and native results appear in one place.

## Concepts to know

- Threat detection
- Posture scores
- Organization-wide enablement
- Delegated administrator account
- Finding aggregation

## Related tools

- [Google Security Command Center](gcp-scc.md) — Posture, misconfiguration, and threat findings for a Google Cloud organization.
- [Microsoft Defender for Cloud](azure-defender.md) — Secure score, recommendations, and workload protection plans for Azure and connected clouds.
