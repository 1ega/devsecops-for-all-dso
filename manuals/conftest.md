# conftest

**Area:** 4. Check infrastructure code → Infrastructure as code  
**License:** Apache-2.0

[GitHub: open-policy-agent/conftest](https://github.com/open-policy-agent/conftest) · [Documentation](https://www.conftest.dev/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/terraform/conftest-examples)

## What it is for

Tests any structured config file against your own Rego policies.

For rules specific to your organization: required labels, allowed registries, naming. The same Rego works for Terraform, Kubernetes YAML, and Dockerfiles.

## Install

**Homebrew or Go**

```bash
brew install conftest
# or
CGO_ENABLED=0 go install github.com/open-policy-agent/conftest@latest
```

## Use

**Test a manifest against a policy directory**

```bash
conftest test -p policy/ deployment.yaml
```

**Terraform with the HCL2 parser**

```bash
conftest test -p policy/ main.tf --parser hcl2
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
conftest:
  stage: test
  image:
    name: openpolicyagent/conftest:latest
    entrypoint: [""]
  script:
    - conftest test -p policy/ k8s/ --output junit > conftest.xml
  artifacts:
    when: always
    reports:
      junit: conftest.xml
```

## Output and triage

Exit code 1 when a `deny` rule fails; with `--fail-on-warn` warnings exit 1 and failures exit 2.

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
- [Trivy (config)](trivy-config.md) — Misconfiguration checks for IaC with the same binary you use for images.
- [terraform-compliance](terraform-compliance.md) — Readable BDD scenarios that a Terraform plan must satisfy.
