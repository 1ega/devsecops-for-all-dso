# Cloudsplaining

**Area:** 8. Secure the cloud → Cloud identity and access  
**License:** BSD-3-Clause

[GitHub: salesforce/cloudsplaining](https://github.com/salesforce/cloudsplaining) · [Documentation](https://cloudsplaining.readthedocs.io/)

## What it is for

Reports AWS IAM policies that allow privilege escalation, data exfiltration, or resource exposure.

Produces a triage-friendly HTML report of risky policies, with an exclusions file to record what you have accepted.

## Install

**pip or Homebrew**

```bash
pip install cloudsplaining
# or
brew install cloudsplaining
```

## Use

**Download the account authorization details and scan them**

```bash
cloudsplaining download --profile my-audit-profile
cloudsplaining create-exclusions-file
cloudsplaining scan --exclusions-file exclusions.yml --input-file default.json --output reports/
```

## Output and triage

Start with policies flagged for privilege escalation and data exfiltration.

## Concepts to know

- Least privilege
- Privilege escalation paths
- Wildcard actions and resources
- Unused access
- Workload identity
- Break-glass accounts

## Related tools

- [PMapper](pmapper.md) — Builds a graph of AWS IAM principals and finds who can escalate to admin.
