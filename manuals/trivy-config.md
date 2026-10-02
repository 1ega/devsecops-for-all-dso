# Trivy (config)

**Area:** 4. Check infrastructure code → Infrastructure as code  
**License:** Apache-2.0

[GitHub: aquasecurity/trivy](https://github.com/aquasecurity/trivy) · [Documentation](https://trivy.dev/docs/latest/)

## What it is for

Misconfiguration checks for IaC with the same binary you use for images.

Avoids adding another tool if Trivy already runs in your pipeline. It replaced the separate tfsec project.

## Install

**Homebrew**

```bash
brew install trivy
```

## Use

**Scan IaC with SARIF output**

```bash
trivy config --format sarif -o trivy-iac.sarif .
```

## Output and triage

Add `--exit-code 1 --severity HIGH,CRITICAL` to gate.

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
- [terraform-compliance](terraform-compliance.md) — Readable BDD scenarios that a Terraform plan must satisfy.
