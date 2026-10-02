# Terraform and IaC

Policies that catch insecure infrastructure before it is applied: missing encryption, public access, disabled logging, overly open network rules, and missing tags.

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| Checkov | [bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) | Many frameworks; custom policies in Python or YAML |
| KICS | [Checkmarx/kics](https://github.com/Checkmarx/kics) | Rego queries, broad coverage |
| Trivy | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Misconfiguration scanning; successor to tfsec |
| conftest | [open-policy-agent/conftest](https://github.com/open-policy-agent/conftest) | Custom Rego policies for any structured config |
| TFLint | [terraform-linters/tflint](https://github.com/terraform-linters/tflint) | Linting and provider-specific rules |

Related skill: [checkov](../../skills/cicd-iac-security/checkov/SKILL.md).

**Status:** Structure only; no policies are published yet.
