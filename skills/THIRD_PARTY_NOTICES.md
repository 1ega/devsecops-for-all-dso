# Third-party notices

Some skills in this directory come from other projects. Each keeps its original license and author in its `SKILL.md` frontmatter.

## Platform Skills

- Source: https://github.com/nitinjain999/platform-skills, commit `5864f06` (v1.42.0)
- Copyright 2026 Nitin Jain
- License: Apache License 2.0, see [licenses/platform-skills-Apache-2.0.txt](licenses/platform-skills-Apache-2.0.txt) and [licenses/platform-skills-NOTICE.txt](licenses/platform-skills-NOTICE.txt)
- Skills: `supply-chain/supply-chain`, `supply-chain/trivy`, `cicd-iac-security/zizmor`, `cicd-iac-security/checkov`, `secrets-management/secrets`, `secrets-management/kingfisher`, `kubernetes-containers/kyverno`, `kubernetes-containers/opa`, `kubernetes-containers/fluxcd-security`, `network-security/aws-waf`, `ai-security/ai-governance`, `detection-response/runtime-security`, `compliance/compliance`

Changes made when importing:

- Only the security-related topics were imported. Each topic became its own skill: `commands/<topic>.md` became `SKILL.md`, `references/<topic>.md` moved to the skill's `references/`, and `examples/<topic>/` moved to the skill's `examples/`.
- `aws-waf` and `fluxcd-security` had no command file upstream. Their `SKILL.md` is the upstream reference with a new name and description.
- Documentation-site frontmatter was replaced with skill frontmatter (`name`, `description`, `argument-hint`, `license`, `metadata`).
- `/platform-skills:<topic>` command links were changed to `/<topic>`. Links to another imported topic now name that skill, and links to topics that were not imported point to the upstream file.

## Trail of Bits skills

- Source: https://github.com/trailofbits/skills, see [trailofbits/SOURCE.md](trailofbits/SOURCE.md) for the commit
- License: CC-BY-SA-4.0, see [trailofbits/LICENSE](trailofbits/LICENSE)
- Plugins: the 23 security-related plugins listed in [trailofbits/README.md](trailofbits/README.md); plugins unrelated to security were not imported.
- Imported unchanged. Changes to these files must be shared under CC-BY-SA-4.0.

## devops-skills

- Author recorded in frontmatter: `devops-skills`
- License recorded in frontmatter: MIT
- Skills: `ai-agent-security`, `ai-coding-agent-guardrails`, `ai-red-teaming`, `ai-security-hardening`, `aws-secrets-manager`, `azure-keyvault`, `cis-benchmarks`, `container-hardening`, `container-scanning`, `dast-scanning`, `dependency-scanning`, `firewall-config`, `gcp-secret-manager`, `hashicorp-vault`, `incident-response`, `kubernetes-hardening`, `linux-hardening`, `llm-app-security`, `mcp-server-security`, `model-supply-chain-security`, `openclaw-deployment-hardening`, `penetration-testing`, `prompt-injection-defense`, `sast-scanning`, `sbom-supply-chain`, `security-automation`, `sops-encryption`, `ssl-tls-management`, `supply-chain-attack-response`, `threat-modeling`, `vpn-setup`, `vulnerability-scanning`, `waf-setup`, `windows-hardening`, `zero-trust`
- Imported unchanged except for "Related Skills" links. Links to skills in this repository now use the new category paths, and links to skills that are not here became plain text.
