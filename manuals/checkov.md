# Checkov

**Area:** 4. Check infrastructure code → Infrastructure as code  
**License:** Apache-2.0  
**Notes:** GitLab SAST output  
**Recommended first choice in this topic.**

[GitHub: bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) · [Documentation](https://www.checkov.io/1.Welcome/Quick%20Start.html) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/terraform)

## What it is for

Over a thousand checks for Terraform, Helm, Kubernetes, CloudFormation, and Dockerfiles.

Broadest coverage in one tool, with checks for Terraform plans (resolved values) as well as source. Custom policies can be written in YAML.

## Install

**pip or Homebrew**

```bash
pip3 install checkov
# or
brew install checkov
```

## Use

**Scan a directory**

```bash
checkov -d .
```

**Scan a Terraform plan**

```bash
terraform plan -out tf.plan
terraform show -json tf.plan > tf.json
checkov -f tf.json
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
checkov:
  stage: test
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d . -o cli -o junitxml --output-file-path console,checkov.xml
  artifacts:
    when: always
    reports:
      junit: checkov.xml
```

## Output and triage

Failed checks fail the job; use `--soft-fail` while you tune, and `--skip-check CKV_AWS_20` or an inline `#checkov:skip=CKV_AWS_20:reason` for accepted risks.

## Concepts to know

- Policy as code
- Terraform plan vs source scans
- Terraform state secrets
- Secure configuration baseline
- Version-controlled configuration
- Drift

## Related tools

- [KICS](kics.md) — Rego queries for Terraform, Helm, Docker, Ansible, and more; behind GitLab IaC SAST.
- [conftest](conftest.md) — Tests any structured config file against your own Rego policies.
- [Trivy (config)](trivy-config.md) — Misconfiguration checks for IaC with the same binary you use for images.
- [terraform-compliance](terraform-compliance.md) — Readable BDD scenarios that a Terraform plan must satisfy.
