# Roadmap

This is a task map for a small or medium team securing **code, builds, artifacts, infrastructure, cloud, running workloads, and response**. Start with [Find by task](README.md#find-by-task) if you have a concrete problem. The interactive roadmap is maintained in the separate `devsecops-roadmap` project for a future Pages release. Each tool's [manual](manuals/README.md) explains use; a manual alone does not mean this repository ships a ready integration.

## Choose a starting point

| Your immediate need | Repository entry point | Current state | Next useful addition |
| :--- | :--- | :--- | :--- |
| Secrets and source code | [gitleaks](scanners/gitleaks/README.md), [Semgrep rules](semgrep-rules/README.md) | Imported and original rule content | Validate mobile and imported packs in CI; define blocking profiles |
| Dependencies, SBOMs, images | [Grype](scanners/grype/README.md), [Trivy](scanners/trivy/README.md), [osv-scanner](scanners/osv-scanner/README.md) | Grype SARIF wrapper; other references | Test fixtures, version pinning, shared triage format |
| CI/CD and artifacts | [CI policies](policies/cicd/README.md), [integrations](integrations/README.md), [supply chain](policies/supply-chain/README.md) | Imported policies; integration scaffolds | Reusable GitHub/GitLab jobs, signing verification |
| Infrastructure and Kubernetes | [Terraform policies](policies/terraform/README.md), [Kubernetes policies](policies/kubernetes/README.md) | Imported policy libraries | Small, tested default policies and exception examples |
| Cloud and identities | [Prowler scanner](scanners/prowler/README.md), [Cloud policies](policies/cloud/README.md), [Prowler mappings](reporting/compliance-mapping/prowler/SOURCE.md) | Multi-cloud scan wrapper and mapping references; policy scaffold | AWS, Azure, GCP least-privilege checks with fixtures |
| Running apps and clusters | [ZAP](scanners/zap/README.md), [Falco](detections/falco/README.md), [YARA](detections/yara/README.md) | ZAP references; Falco deployment and triage guidance; imported YARA rules | Validate runtime rules and tune YARA with sample events and files |
| Findings and response | [Reporting](reporting/README.md), [playbooks](playbooks/README.md), [threat models](templates/threat-models/README.md) | Standard mappings and templates; draft metadata | Common severity, owner and SLA fields; incident playbooks |

## Delivery order

1. **Make the existing content trustworthy.** Add link checks and CI validation for the mobile, elttam, and Trail of Bits Semgrep packs. Finish [severity and metadata](reporting/severity-and-metadata.md), including ownership and exception fields.
2. **Make high-use tools repeatable.** Add synthetic fixtures and documented output to Grype, Falco, gitleaks, Trivy, [imported YARA packs](detections/yara/README.md), and cloud checks. Pin tool versions in runnable CI examples. Expand the [91 manuals](manuals/README.md) where operators need tuning and triage steps.
3. **Connect the controls.** Build reusable [GitHub Actions and GitLab CI integrations](integrations/README.md), pre-commit hooks, a `dso` entry point, and finding import to DefectDojo. A local command and its CI job should produce the same result format.
4. **Cover environments after deploy.** Turn imported Kubernetes and IaC references into tested default policies; add AWS, Azure, and GCP checks; validate Falco rules and alert routing; add DAST examples for owned web apps and APIs.
5. **Close the loop.** Link findings to [compliance mappings](reporting/compliance-mapping/README.md), [threat models](templates/threat-models/README.md), and [response playbooks](playbooks/README.md). Add safe labs so teams can rehearse a detection and a fix.

For each new control, add a [research note](docs/research/README.md), a runnable example or fixture, expected output, tuning guidance, source/license details, and a README entry. The [contribution guide](CONTRIBUTING.md) describes the review requirements.
