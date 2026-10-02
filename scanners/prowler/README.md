# Prowler cloud posture scan

**Status:** Repository entry point for AWS, Azure, GCP, and Kubernetes assessment. Prowler is an external tool; [framework mappings](../../reporting/compliance-mapping/prowler/SOURCE.md) are already imported here.

Use an authorized, read-only identity with the permissions needed for the selected checks. Prefer short-lived role or workload identity credentials. Follow the [full Prowler manual](../../manuals/prowler.md) for installation, provider authentication, and framework selection.

## Run

Pin a reviewed Prowler version. Choose an output directory outside the repository because reports can contain resource names and configuration details.

```bash
# From the repository root, after configuring an authorized AWS identity
bash scanners/prowler/scan.sh aws "$HOME/prowler-reports" --compliance pci_4.0_aws

# Scan one GCP project with an authorized identity
bash scanners/prowler/scan.sh gcp "$HOME/prowler-reports-gcp" --project-ids my-project
```

The wrapper writes JSON OCSF and HTML, leaves Prowler's exit status intact, and creates files with a restrictive process umask. A failed check may produce Prowler exit code `3`; review the report and keep it in an approved location. Confirm coverage and API permission errors before calling an account compliant. See [Prowler CLI documentation](https://docs.prowler.com/) and the local [compliance mappings](../../reporting/compliance-mapping/prowler/SOURCE.md).
