# Microsoft Defender for Cloud

**Area:** 8. Secure the cloud → Native cloud security services  
**License:** Azure service

[Documentation](https://learn.microsoft.com/azure/defender-for-cloud/)

## What it is for

Secure score, recommendations, and workload protection plans for Azure and connected clouds.

The free tier gives posture recommendations and a secure score; paid plans add threat protection per workload type.

## Install

**Enable a Defender plan for a subscription**

```bash
az security pricing create -n VirtualMachines --tier standard
```

## Use

**List alerts**

```bash
az security alert list -o table
```

## Concepts to know

- Threat detection
- Posture scores
- Organization-wide enablement
- Delegated administrator account
- Finding aggregation

## Related tools

- [AWS Security Hub and GuardDuty](aws-security-hub.md) — Security Hub aggregates findings and runs standards; GuardDuty detects threats from logs.
- [Google Security Command Center](gcp-scc.md) — Posture, misconfiguration, and threat findings for a Google Cloud organization.
