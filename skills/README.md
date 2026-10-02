# AI skills

Reusable instructions for AI coding agents, grouped by security domain. Each skill lives in `skills/<category>/<skill>/` and has a self-contained `SKILL.md` with a name and description for discovery. Some skills include `references/`, `scripts/`, `assets/`, or `examples/` next to `SKILL.md`.

| Category | Skills | Covers |
| :--- | :---: | :--- |
| [appsec-testing](#appsec-testing) | 8 | Pentest, code review, SAST, DAST, threat modeling, vulnerability scanning |
| [supply-chain](#supply-chain) | 6 | Dependencies, containers, SBOM, signing, supply chain incidents |
| [cicd-iac-security](#cicd-iac-security) | 3 | Pipeline security gates, GitHub Actions audit, Terraform scanning |
| [secrets-management](#secrets-management) | 7 | Cloud secret stores, Vault, SOPS, Kubernetes secrets, leaked secret response |
| [kubernetes-containers](#kubernetes-containers) | 5 | Image and runtime hardening, admission policy, GitOps security |
| [host-hardening](#host-hardening) | 4 | Linux, Windows, CIS benchmarks, deployment preflight |
| [network-security](#network-security) | 6 | Firewalls, VPN, WAF, TLS, zero trust |
| [ai-security](#ai-security) | 9 | Agents, LLM apps, MCP, prompt injection, AI red teaming, model supply chain |
| [detection-response](#detection-response) | 2 | Incident response and runtime threat detection |
| [compliance](#compliance) | 1 | SOC 2 controls and evidence for Terraform |
| [trailofbits](trailofbits/README.md) | 23 plugins | Imported Trail of Bits plugins: Semgrep rule creation, static analysis and SARIF, variant analysis, insecure defaults, supply-chain risk, false-positive checks, language-specific security review |

## appsec-testing

| Skill | Use it for |
| :--- | :--- |
| [authorized-pentest](appsec-testing/authorized-pentest/SKILL.md) | Planning and carrying out a scoped, authorized assessment and reporting evidence |
| [penetration-testing](appsec-testing/penetration-testing/SKILL.md) | Reconnaissance, vulnerability discovery, and validation of security controls |
| [secure-code-review](appsec-testing/secure-code-review/SKILL.md) | Reviewing code changes for security and quality defects with actionable findings |
| [threat-modeling](appsec-testing/threat-modeling/SKILL.md) | STRIDE threat modeling, risk assessment, and control design |
| [sast-scanning](appsec-testing/sast-scanning/SKILL.md) | Static analysis with Semgrep, CodeQL, and SonarQube |
| [dast-scanning](appsec-testing/dast-scanning/SKILL.md) | Dynamic testing with OWASP ZAP, Burp Suite, and Nikto |
| [security-dast](appsec-testing/security-dast/SKILL.md) | Playwright-driven OWASP Top 10, header, cookie, XSS, SQLi, and CSRF checks |
| [vulnerability-scanning](appsec-testing/vulnerability-scanning/SKILL.md) | CVE scanning and prioritization with Nessus, OpenVAS, Qualys, and Trivy |

## supply-chain

| Skill | Use it for |
| :--- | :--- |
| [dependency-scanning](supply-chain/dependency-scanning/SKILL.md) | Software composition analysis with Snyk, Dependabot, and OWASP Dependency-Check |
| [container-scanning](supply-chain/container-scanning/SKILL.md) | Image vulnerability scanning with Trivy, Grype, and cloud-native scanners |
| [trivy](supply-chain/trivy/SKILL.md) | Trivy image, filesystem, repo, SBOM, and in-cluster scanning with CI gates |
| [sbom-supply-chain](supply-chain/sbom-supply-chain/SKILL.md) | Generating, signing, and verifying SBOMs and provenance attestations |
| [supply-chain](supply-chain/supply-chain/SKILL.md) | Cosign signing, Syft SBOMs, SLSA provenance, and admission enforcement |
| [supply-chain-attack-response](supply-chain/supply-chain-attack-response/SKILL.md) | Detecting and responding to compromised packages, images, and pipelines |

## cicd-iac-security

| Skill | Use it for |
| :--- | :--- |
| [security-automation](cicd-iac-security/security-automation/SKILL.md) | Security pipelines, automated remediation, and SOAR-style workflows |
| [zizmor](cicd-iac-security/zizmor/SKILL.md) | Auditing GitHub Actions for template injection, unpinned actions, and broad permissions |
| [checkov](cicd-iac-security/checkov/SKILL.md) | Static and plan-level Terraform security scanning with fix suggestions |

## secrets-management

| Skill | Use it for |
| :--- | :--- |
| [aws-secrets-manager](secrets-management/aws-secrets-manager/SKILL.md) | Storing and rotating secrets in AWS Secrets Manager |
| [azure-keyvault](secrets-management/azure-keyvault/SKILL.md) | Secrets and certificates in Azure Key Vault |
| [gcp-secret-manager](secrets-management/gcp-secret-manager/SKILL.md) | Secrets, IAM, and GKE integration in Google Cloud Secret Manager |
| [hashicorp-vault](secrets-management/hashicorp-vault/SKILL.md) | Vault secret engines, auth methods, policies, and PKI |
| [sops-encryption](secrets-management/sops-encryption/SKILL.md) | Encrypting files and configs with SOPS |
| [secrets](secrets-management/secrets/SKILL.md) | External Secrets Operator, Sealed Secrets, rotation runbooks, and Kubernetes secrets audit |
| [kingfisher](secrets-management/kingfisher/SKILL.md) | Finding, validating, scoping, and revoking leaked secrets |

## kubernetes-containers

| Skill | Use it for |
| :--- | :--- |
| [container-hardening](kubernetes-containers/container-hardening/SKILL.md) | Non-root, read-only, minimal container images and runtime settings |
| [kubernetes-hardening](kubernetes-containers/kubernetes-hardening/SKILL.md) | Security contexts, Pod Security Standards, and network policies |
| [kyverno](kubernetes-containers/kyverno/SKILL.md) | Writing, testing, and migrating CEL-based Kyverno policies |
| [opa](kubernetes-containers/opa/SKILL.md) | OPA Rego and Conftest policies with tests and CI integration |
| [fluxcd-security](kubernetes-containers/fluxcd-security/SKILL.md) | Security audit checklist for Flux CD GitOps repositories |

## host-hardening

| Skill | Use it for |
| :--- | :--- |
| [linux-hardening](host-hardening/linux-hardening/SKILL.md) | CIS-aligned Linux server hardening and audit |
| [windows-hardening](host-hardening/windows-hardening/SKILL.md) | Windows Server baselines, Group Policy, and Defender |
| [cis-benchmarks](host-hardening/cis-benchmarks/SKILL.md) | Automated CIS benchmark assessment and remediation |
| [openclaw-deployment-hardening](host-hardening/openclaw-deployment-hardening/SKILL.md) | Preflight checks, runtime restrictions, and post-deploy verification for OpenClaw |

## network-security

| Skill | Use it for |
| :--- | :--- |
| [firewall-config](network-security/firewall-config/SKILL.md) | iptables, nftables, UFW, and cloud firewall rules |
| [vpn-setup](network-security/vpn-setup/SKILL.md) | WireGuard, OpenVPN, and cloud VPN tunnels |
| [waf-setup](network-security/waf-setup/SKILL.md) | Deploying and tuning WAFs for OWASP Top 10 protection |
| [aws-waf](network-security/aws-waf/SKILL.md) | AWS WAF web ACLs, managed rules, rate limiting, logging, and Shield |
| [ssl-tls-management](network-security/ssl-tls-management/SKILL.md) | Certificates with Let's Encrypt and internal PKI |
| [zero-trust](network-security/zero-trust/SKILL.md) | Zero-trust network architecture and identity-based access |

## ai-security

| Skill | Use it for |
| :--- | :--- |
| [ai-agent-security](ai-security/ai-agent-security/SKILL.md) | Defense in depth for tool-using AI agents |
| [ai-coding-agent-guardrails](ai-security/ai-coding-agent-guardrails/SKILL.md) | Permission boundaries and review gates for coding agents |
| [ai-governance](ai-security/ai-governance/SKILL.md) | Session hooks and merge-time policy gates for AI coding agents |
| [ai-red-teaming](ai-security/ai-red-teaming/SKILL.md) | Structured jailbreak, exfiltration, and tool abuse exercises |
| [ai-security-hardening](ai-security/ai-security-hardening/SKILL.md) | Hardening production AI and LLM deployments |
| [llm-app-security](ai-security/llm-app-security/SKILL.md) | Input and output controls, tenant isolation, and abuse prevention for LLM apps |
| [mcp-server-security](ai-security/mcp-server-security/SKILL.md) | Transport, authorization, validation, and audit for MCP servers |
| [prompt-injection-defense](ai-security/prompt-injection-defense/SKILL.md) | Direct and indirect prompt injection defenses |
| [model-supply-chain-security](ai-security/model-supply-chain-security/SKILL.md) | Model signing, provenance, and trusted promotion |

## detection-response

| Skill | Use it for |
| :--- | :--- |
| [incident-response](detection-response/incident-response/SKILL.md) | IR playbooks, evidence collection, containment, and recovery |
| [runtime-security](detection-response/runtime-security/SKILL.md) | Falco rules, alert routing, and runtime-to-admission enforcement |

## compliance

| Skill | Use it for |
| :--- | :--- |
| [compliance](compliance/compliance/SKILL.md) | SOC 2 gap analysis, controls, and evidence for Terraform |

## trailofbits

[23 security plugins](trailofbits/README.md) from Trail of Bits, kept as complete Claude Code plugins rather than split into the categories above. Highlights: [semgrep-rule-creator](trailofbits/semgrep-rule-creator/README.md), [static-analysis](trailofbits/static-analysis/README.md), [variant-analysis](trailofbits/variant-analysis/README.md), [fp-check](trailofbits/fp-check/README.md), [insecure-defaults](trailofbits/insecure-defaults/README.md), [supply-chain-risk-auditor](trailofbits/supply-chain-risk-auditor/README.md), and [agentic-actions-auditor](trailofbits/agentic-actions-auditor/README.md).

## Using a skill

For Claude Code or Codex, copy a skill directory (for example `skills/appsec-testing/threat-modeling/`) into your agent's skills folder and refresh skill discovery. For another agent, include the `SKILL.md` as task instructions. These files do not grant access to targets or replace a written assessment scope.

Scripts under `scripts/`, `assets/`, and `examples/` can change system state. Read them and run them in dry-run mode or a disposable environment first.

## Sources and licenses

Third-party skills keep their original license and author in the `SKILL.md` frontmatter. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for sources and the changes made when importing them.
