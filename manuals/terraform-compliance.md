# terraform-compliance

**Area:** 4. Check infrastructure code → Infrastructure as code  
**License:** MIT

[GitHub: terraform-compliance/cli](https://github.com/terraform-compliance/cli) · [Documentation](https://terraform-compliance.com)

## What it is for

Readable BDD scenarios that a Terraform plan must satisfy.

Lets security and compliance teams write rules in plain Given/When/Then sentences that engineers can read and review.

## Install

**pip**

```bash
pip install terraform-compliance
```

## Use

**Check a plan against feature files**

```bash
terraform show -json plan.out > plan.out.json
terraform-compliance -f features/ -p plan.out.json
```

## Output and triage

Failed scenarios exit non-zero; `--no-failures` forces 0 while you introduce rules.

## Concepts to know

- Policy as code
- Terraform plan vs source scans
- Terraform state secrets
- Secure configuration baseline
- Version-controlled configuration
- Drift

## Related tools

- [Checkov](checkov.md) — Over a thousand checks for Terraform, Helm, Kubernetes, CloudFormation, and Dockerfiles.
- [KICS](kics.md) — Rego queries for Terraform, Helm, Docker, Ansible, and more; behind GitLab IaC SAST.
- [conftest](conftest.md) — Tests any structured config file against your own Rego policies.
- [Trivy (config)](trivy-config.md) — Misconfiguration checks for IaC with the same binary you use for images.
