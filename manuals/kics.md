# KICS

**Area:** 4. Check infrastructure code → Infrastructure as code  
**License:** Apache-2.0  
**Notes:** GitLab SAST output (glsast)

[GitHub: Checkmarx/kics](https://github.com/Checkmarx/kics) · [Documentation](https://docs.kics.io/)

## What it is for

Rego queries for Terraform, Helm, Docker, Ansible, and more; behind GitLab IaC SAST.

The engine GitLab uses for IaC scanning. Running it directly lets you pick report formats and severity gates.

> [!WARNING]
> In March and April 2026 KICS GitHub Actions and Docker Hub images were reported compromised. Pin by digest and verify.

## Install

**Container image**

```bash
docker pull checkmarx/kics:latest
```

## Use

**Scan a directory**

```bash
docker run -t -v "$PWD":/path checkmarx/kics scan -p /path -o /path/
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
kics:
  stage: test
  image:
    name: checkmarx/kics:latest        # pin by digest
    entrypoint: [""]
  script:
    - kics scan -p "$CI_PROJECT_DIR" --ignore-on-exit all
        --report-formats glsast -o "$CI_PROJECT_DIR" --output-name kics-results
  artifacts:
    reports:
      sast: gl-sast-kics-results.json
```

## Output and triage

Exit codes encode the highest severity found (60 critical, 50 high, 40 medium, 30 low); `--fail-on high` and `--ignore-on-exit` control gating.

## Concepts to know

- Policy as code
- Terraform plan vs source scans
- Terraform state secrets
- Secure configuration baseline
- Version-controlled configuration
- Drift

## Related tools

- [Checkov](checkov.md) — Over a thousand checks for Terraform, Helm, Kubernetes, CloudFormation, and Dockerfiles.
- [conftest](conftest.md) — Tests any structured config file against your own Rego policies.
- [Trivy (config)](trivy-config.md) — Misconfiguration checks for IaC with the same binary you use for images.
- [terraform-compliance](terraform-compliance.md) — Readable BDD scenarios that a Terraform plan must satisfy.
