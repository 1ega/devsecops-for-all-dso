# Manuals

Practical manuals for the scanners and platforms used across this repository: how to install and configure a tool, run it locally and in CI, read its output, and tune it. A manual explains the tool; the ready-to-use configuration itself lives in [`scanners/`](../scanners/README.md), [`policies/`](../policies/README.md), or [`integrations/`](../integrations/README.md).

Write one file per tool, `manuals/<tool>.md`, using the [template](TEMPLATE.md).

## Planned manuals

| Area | Tools |
| :--- | :--- |
| Secrets | gitleaks, betterleaks, TruffleHog |
| Dependencies and SBOM | Trivy, osv-scanner, Grype, syft, cdxgen, Dependency-Track |
| Static analysis | Semgrep, Opengrep, CodeQL, gosec, find-sec-bugs |
| Mobile builds | MobSF, mobsfscan, jadx, apktool |
| CI/CD | poutine, zizmor, actionlint, pinact, OpenSSF Scorecard |
| Infrastructure as code | Checkov, KICS, conftest / OPA, kube-linter |
| Containers | hadolint, Dockle |
| Kubernetes | Kyverno, Gatekeeper, Chainsaw, Kubescape, kube-bench |
| Supply chain | cosign, witness, slsa-verifier, sbomqs |
| Dynamic testing | ZAP, nuclei, Schemathesis |
| Cloud | Prowler |
| Threat modeling | pytm, Threagile, Threat Dragon |
| Vulnerability management | DefectDojo, secureCodeBox |

| Manual | Status |
| :--- | :--- |
| — | No manuals yet |
