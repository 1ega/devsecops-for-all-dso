# KICS

**Version reviewed:** v2.2.0 ([official release](https://github.com/Checkmarx/kics/releases/tag/v2.2.0)); metadata checked 2026-10-02.

**Area:** 4. Check infrastructure code → Infrastructure as code  
**License:** Apache-2.0  
**Notes:** GitLab SAST output (glsast)

[GitHub: Checkmarx/kics](https://github.com/Checkmarx/kics) · [Documentation](https://docs.kics.io/)

## What it is for

Rego queries for Terraform, Helm, Docker, Ansible, and more; behind GitLab IaC SAST.

The engine GitLab uses for IaC scanning. Running it directly lets you pick report formats and severity gates.

> [!WARNING]
> In March and April 2026 KICS GitHub Actions and Docker Hub images were reported compromised. Docker Hub images stop at v2.1.20, last updated on 2026-04-22 inside that window, and v2.2.0 publishes no image or binary. Do not pull `checkmarx/kics:latest`; build the reviewed tag yourself.

## Install

**Build from source** (Go 1.26.2 or later; the same flags as the official Dockerfile)

```bash
git clone --depth 1 --branch v2.2.0 https://github.com/Checkmarx/kics.git
cd kics
CGO_ENABLED=0 go build -ldflags "-X github.com/Checkmarx/kics/v2/internal/constants.Version=v2.2.0" \
  -o ./bin/kics cmd/console/main.go
./bin/kics version
```

## Use

**Scan a directory** (run from the checkout, which provides `assets/queries`)

```bash
./bin/kics scan -p /path/to/iac -o /private/reports --report-formats json,sarif
```

## CI example

Build an image from the reviewed tag's Dockerfile in a trusted pipeline, push it to your registry and pin that digest.

### GitLab CI

```yaml
kics:
  stage: test
  image:
    name: registry.example/security/kics:v2.2.0@sha256:DIGEST  # your build of the v2.2.0 tag
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
