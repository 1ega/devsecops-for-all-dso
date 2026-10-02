# CloudSploit

**Area:** 8. Secure the cloud → Cloud posture (CSPM)  
**License:** GPL-3.0

[GitHub: aquasecurity/cloudsploit](https://github.com/aquasecurity/cloudsploit) · [Documentation](https://github.com/aquasecurity/cloudsploit#readme)

## What it is for

Configuration checks for AWS, Azure, GCP, and Oracle Cloud with compliance filters.

A lightweight alternative to Prowler that can filter results to HIPAA, PCI, or CIS controls.

## Install

**From source (Node.js)**

```bash
git clone https://github.com/aquasecurity/cloudsploit.git
cd cloudsploit && npm install
```

## Use

**Run PCI checks**

```bash
./index.js --config ./config.js --compliance=pci --json results.json
```

## Output and triage

Copy `config_example.js` to `config.js` and point it at read-only credentials first.

## Concepts to know

- IAM and least privilege
- Cloud activity logs
- Landing zone and organization policy
- Network segmentation
- Encryption by default
- Public exposure

## Related tools

- [Prowler](prowler.md) — Hundreds of checks for AWS, Azure, GCP, and Kubernetes, mapped to CIS, PCI DSS, ISO 27001, and more.
- [ScoutSuite](scoutsuite.md) — Multi-cloud audit that builds an offline HTML report of risky configuration.
- [Cloud Custodian](cloud-custodian.md) — YAML policies that find and optionally fix non-compliant cloud resources.
- [Steampipe and Powerpipe](steampipe.md) — Query cloud APIs with SQL and run compliance benchmarks with dashboards.
