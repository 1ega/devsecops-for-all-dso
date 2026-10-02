# Prowler

**Area:** 8. Secure the cloud → Cloud posture (CSPM)  
**License:** Apache-2.0  
**Notes:** Upstream GitLab CI cookbook  
**Recommended first choice in this topic.**

[GitHub: prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) · [Documentation](https://docs.prowler.com/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/reporting/compliance-mapping/prowler)

## What it is for

Hundreds of checks for AWS, Azure, GCP, and Kubernetes, mapped to CIS, PCI DSS, ISO 27001, and more.

Answers "are we compliant?" per framework out of the box. The framework mappings are imported in this repository.

## Install

**pip, pipx, or Homebrew**

```bash
pip install prowler
# or
brew install prowler
```

## Use

**AWS against PCI DSS 4.0**

```bash
prowler aws --compliance pci_4.0_aws -M csv json-ocsf html -o reports/
```

**Other providers**

```bash
prowler gcp --project-ids my-project
prowler azure --az-cli-auth
prowler kubernetes --kubeconfig-file ~/.kube/config
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
prowler:
  stage: test
  image: python:3.13-slim
  before_script:
    - pip install prowler
  script:
    # use a read-only role; prefer id_tokens + AssumeRoleWithWebIdentity over static keys
    - prowler aws --compliance cis_6.0_aws -M json-ocsf html -o reports/ -z
  artifacts:
    when: always
    paths: [reports/]
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"
```

## Output and triage

Exit code 3 when checks fail; `-z` ignores it so the report is always kept. List frameworks with `prowler aws --list-compliance`.

## Concepts to know

- IAM and least privilege
- Cloud activity logs
- Landing zone and organization policy
- Network segmentation
- Encryption by default
- Public exposure

## Related tools

- [ScoutSuite](scoutsuite.md) — Multi-cloud audit that builds an offline HTML report of risky configuration.
- [Cloud Custodian](cloud-custodian.md) — YAML policies that find and optionally fix non-compliant cloud resources.
- [Steampipe and Powerpipe](steampipe.md) — Query cloud APIs with SQL and run compliance benchmarks with dashboards.
- [CloudSploit](cloudsploit.md) — Configuration checks for AWS, Azure, GCP, and Oracle Cloud with compliance filters.
