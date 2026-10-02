# Policies

Policy-as-code packs for infrastructure and delivery controls belong here, organized by target and then by policy engine when needed.

| Directory | Target | Candidate engines |
| :--- | :--- | :--- |
| [terraform](terraform/README.md) | Terraform, Helm, CloudFormation before apply | Checkov, KICS, Trivy, conftest |
| [kubernetes](kubernetes/README.md) | Admission control and cluster audits | Kyverno, Gatekeeper, kube-bench |
| [containers](containers/README.md) | Dockerfiles and images | hadolint, Trivy, Dockle |
| [cicd](cicd/README.md) | GitHub Actions and GitLab CI pipelines | zizmor, poutine, actionlint |
| [cloud](cloud/README.md) | Deployed AWS, GCP, and Azure accounts | Prowler, Cloud Custodian |
| [supply-chain](supply-chain/README.md) | SBOMs, signatures, provenance | syft, cosign, SLSA |

Each policy should explain the control, include allowed and denied examples, and document how to test and apply it. Prefer reviewable defaults over environment-specific assumptions.

**Status:** Structure only; no policy packs are published yet.
