# Trivy config fixtures

Original Terraform fixtures: `bad/main.tf` allows internet SSH; `good/main.tf`
limits the test rule to an internal subnet. Neither is applied to a cloud account.

With reviewed Trivy 0.75.0 installed, run from the repository root:

```bash
bash scanners/trivy/scan.sh config scanners/trivy/tests/bad /private/reports/bad
# Expected exit 1 and HIGH misconfiguration in trivy-config.sarif.
bash scanners/trivy/scan.sh config scanners/trivy/tests/good /private/reports/good
# Expected exit 0 and no gated HIGH/CRITICAL result.
```

Tool/cache/network failures return 2. Record the check-bundle version; use current
checks in deployment pipelines. These fixtures test the SSH exposure boundary,
not the entire AWS network design. The intentionally insecure fixture will be
found if you scan this whole toolbox; scan application/IaC targets in production.
