# Google Security Command Center

**Area:** 8. Secure the cloud → Native cloud security services  
**License:** Google Cloud service

[Documentation](https://cloud.google.com/security-command-center/docs)

## What it is for

Posture, misconfiguration, and threat findings for a Google Cloud organization.

Enabled once at the organization level, it covers every project, including ones created later.

## Install

**Activate at the organization level in the Google Cloud console**

```bash
# Security Command Center > Get started (organization admin required)
```

## Use

**List active findings**

```bash
gcloud scc findings list organizations/ORGANIZATION_ID --filter='state="ACTIVE"'
```

## Concepts to know

- Threat detection
- Posture scores
- Organization-wide enablement
- Delegated administrator account
- Finding aggregation

## Related tools

- [AWS Security Hub and GuardDuty](aws-security-hub.md) — Security Hub aggregates findings and runs standards; GuardDuty detects threats from logs.
- [Microsoft Defender for Cloud](azure-defender.md) — Secure score, recommendations, and workload protection plans for Azure and connected clouds.
