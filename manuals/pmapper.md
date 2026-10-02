# PMapper

**Area:** 8. Secure the cloud → Cloud identity and access  
**License:** AGPL-3.0  
**Recommended first choice in this topic.**

[GitHub: nccgroup/PMapper](https://github.com/nccgroup/PMapper) · [Documentation](https://github.com/nccgroup/PMapper/wiki)

## What it is for

Builds a graph of AWS IAM principals and finds who can escalate to admin.

Answers the question that matters in an incident: who can actually reach admin, directly or through role chains.

## Install

**pip**

```bash
pip install principalmapper
```

## Use

**Build the graph for an account**

```bash
pmapper --profile my-audit-profile graph create
```

**Find privilege escalation paths**

```bash
pmapper --profile my-audit-profile query 'preset privesc *'
pmapper --profile my-audit-profile query 'who can do iam:CreateUser'
```

## Output and triage

Review every non-admin principal that can reach admin. Last updated in 2024, so check results against current AWS behavior.

## Concepts to know

- Least privilege
- Privilege escalation paths
- Wildcard actions and resources
- Unused access
- Workload identity
- Break-glass accounts

## Related tools

- [Cloudsplaining](cloudsplaining.md) — Reports AWS IAM policies that allow privilege escalation, data exfiltration, or resource exposure.
