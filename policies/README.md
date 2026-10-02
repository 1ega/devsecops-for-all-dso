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

Imported policy libraries:

| Library | Contents | License |
| :--- | :--- | :--- |
| [kubernetes/kyverno-policies](kubernetes/kyverno-policies/SOURCE.md) | Kyverno community library: pod security, best practices, and add-on specific policies, with Chainsaw tests | Apache-2.0 |
| [kubernetes/gatekeeper-library](kubernetes/gatekeeper-library/SOURCE.md) | 49 Gatekeeper constraint templates with samples, including pod security policies | Apache-2.0 |
| [cicd/poutine-rego](cicd/poutine-rego/SOURCE.md) | 26 Rego rules for pipeline weaknesses in GitHub Actions, GitLab CI, Azure Pipelines, and Tekton | Apache-2.0 |
| [terraform/conftest-examples](terraform/conftest-examples/SOURCE.md) | Example Rego policies and inputs for Terraform, Kubernetes, Dockerfiles, and more | Apache-2.0 |
| [containers/distroless-examples](containers/distroless-examples/SOURCE.md) | Reference multi-stage Dockerfiles on distroless base images | Apache-2.0 |
| [supply-chain/sigstore-policy-controller](supply-chain/sigstore-policy-controller/SOURCE.md) | Example ClusterImagePolicy resources for signature and attestation checks | Apache-2.0 |

Each policy should explain the control, include allowed and denied examples, and document how to test and apply it. Prefer reviewable defaults over environment-specific assumptions.

**Status:** Upstream libraries imported; policy packs of our own are not published yet.
