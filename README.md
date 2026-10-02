<div align="center">
  <img src="assets/banner.svg" alt="DevSecOps for All — the security Swiss Army knife" width="100%">

  # DevSecOps for All

  ### The DevSecOps Swiss Army knife

</div>

DevSecOps for All collects security checks, policies, detection rules, standards, and manuals in one place, so a team can scan its code, cloud accounts, and clusters, enforce controls, hunt for malware, and know what to do with each finding.

> 🗺️ **[Explore the interactive DevSecOps roadmap →](https://1ega.github.io/devsecopsforall/)**
>
> Browse 9 security areas and 91 tools, with installation steps, usage examples, and full manuals.

**[Quick start](#quick-start)** · **[Interactive roadmap](https://1ega.github.io/devsecopsforall/)** · **[Find by task](#find-by-task)** · **[What's inside](#whats-inside)** · **[How the repository is organized](#how-the-repository-is-organized)** · **[Roadmap](ROADMAP.md)** · **[Contributing](#contributing)**

## Quick start

1. Clone the repository.
2. Pick your task in [Find by task](#find-by-task), or browse [What's inside](#whats-inside).
3. Open that directory's README. Each one says what is there, which tool runs it, and how.

A few examples from different parts of the toolbox, run from the repository root:

```bash
# Find secrets in a project with the gitleaks default rules
gitleaks dir --config rules/secrets/gitleaks-default/gitleaks.toml path/to/project

# Check Kubernetes manifests against example Rego policies
conftest test --policy policies/terraform/conftest-examples/examples/kubernetes/policy path/to/deployment.yaml

# Scan a mobile app's source code
semgrep scan --metrics=off --config rules/semgrep/mobile/rules/ path/to/mobile-app

# Look for known malware in a directory with one YARA rule file
yara -r rules/yara/bartblaze/rules/crimeware/AveMaria.yar path/to/files
```

Run tools only against systems you are authorized to assess, and treat every finding as a lead to verify.

## Find by task

| I want to… | Start here |
| :--- | :--- |
| Scan source code for vulnerabilities | [Semgrep rule packs](rules/semgrep/README.md) · [Python rules](rules/semgrep/python/README.md) |
| Review a mobile app | [Mobile rules](rules/semgrep/mobile/README.md) · [OWASP MASTG](guides/owasp-mastg/SOURCE.md) · [MobSF notes](scanners/mobsf/README.md) |
| Find leaked secrets | [gitleaks](scanners/gitleaks/README.md) · [Secret pattern database](rules/secrets/secrets-patterns-db/SOURCE.md) |
| Check dependencies and SBOMs | [Grype SARIF wrapper](scanners/grype/README.md) · [osv-scanner](scanners/osv-scanner/README.md) · [Trivy](scanners/trivy/README.md) · [Supply chain policies](policies/supply-chain/README.md) |
| Secure CI/CD pipelines | [CI/CD policies](policies/cicd/README.md) · [CI integrations](integrations/README.md) |
| Check Terraform and other IaC | [Terraform policies](policies/terraform/README.md) |
| Harden containers and Kubernetes | [Container policies](policies/containers/README.md) · [Kyverno and Gatekeeper libraries](policies/kubernetes/README.md) |
| Audit a cloud account | [Prowler scan wrapper](scanners/prowler/README.md) · [Prowler frameworks](reporting/compliance-mapping/prowler/SOURCE.md) · [Cloud policies](policies/cloud/README.md) |
| Hunt for malware and malicious code | [YARA rules](rules/yara/README.md) · [GuardDog](manuals/guarddog.md) · [ClamAV](manuals/clamav.md) |
| Test a running web app or API | [ZAP](scanners/zap/README.md) · [nuclei](scanners/nuclei/README.md) |
| Map work to a standard (MASVS, ASVS, PCI DSS, CIS) | [Compliance mapping](reporting/compliance-mapping/README.md) |
| Model threats for a feature | [Threat model templates and examples](templates/threat-models/README.md) |
| Fix or triage a finding | [OWASP Cheat Sheets](guides/owasp-cheatsheets/SOURCE.md) · [Playbooks](playbooks/README.md) · [Severity scale](reporting/severity-and-metadata.md) |
| Respond to an incident | [Playbooks](playbooks/README.md) · [Incident response skill](skills/detection-response/incident-response/SKILL.md) |
| Detect threats in running containers | [Falco deployment and triage](rules/falco/README.md) · [Runtime security examples](skills/detection-response/runtime-security/examples/runtime-security/README.md) |
| Give an AI agent security skills | [Skill catalog](skills/README.md) · [Trail of Bits plugins](skills/trailofbits/README.md) |
| Learn how to install and run a tool | [Manuals for 91 tools](manuals/README.md), each linked to its GitHub repository |

## What's inside

**Status:** ✅ ready — our own content, documented and tested · 📦 imported — upstream content with its license and source recorded · 🗺️ planned — structure and plan only.

### Scan

| Directory | Contents | Status |
| :--- | :--- | :--- |
| [`rules/`](rules/README.md) | All rule sets, by engine: Semgrep ([mobile](rules/semgrep/mobile/README.md) 320, [Python](rules/semgrep/python/README.md) 3, [Trail of Bits](rules/semgrep/trailofbits/SOURCE.md) 120, [elttam](rules/semgrep/elttam/SOURCE.md) 107), [YARA](rules/yara/README.md) (5 sets, about 2,700 files), [secret patterns](rules/README.md), [nuclei templates](rules/nuclei/fuzzing-templates/SOURCE.md), [Falco](rules/falco/README.md) | ✅ · 📦 |
| [`scanners/`](scanners/README.md) | Grype and Prowler wrappers; configuration notes for gitleaks, osv-scanner, Trivy, ZAP, nuclei, MobSF; 200+ ZAP community scripts | ✅ · 📦 · 🗺️ |

### Enforce

| Directory | Contents | Status |
| :--- | :--- | :--- |
| [`policies/kubernetes/`](policies/kubernetes/README.md) | Kyverno community library with tests; 49 Gatekeeper constraint templates | 📦 |
| [`policies/cicd/`](policies/cicd/README.md) | 26 poutine Rego rules for GitHub Actions, GitLab CI, Azure Pipelines, Tekton | 📦 |
| [`policies/terraform/`](policies/terraform/README.md) | conftest example policies for Terraform, Kubernetes, Dockerfiles | 📦 |
| [`policies/containers/`](policies/containers/README.md) | Reference distroless Dockerfiles | 📦 |
| [`policies/supply-chain/`](policies/supply-chain/README.md) | Sigstore policy-controller examples for signature checks | 📦 |
| [`policies/cloud/`](policies/cloud/README.md) | AWS, GCP, and Azure checks | 🗺️ |
| [`integrations/`](integrations/README.md) | GitHub Actions workflow, GitLab CI template, pre-commit hooks, DefectDojo import | 🗺️ |
| [`tools/`](tools/README.md) | Standalone utilities, starting with the [`dso`](tools/dso/README.md) command-line entry point | 🗺️ |

### Know

| Directory | Contents | Status |
| :--- | :--- | :--- |
| [`guides/`](guides/README.md) | Security review and pentest planning checklists | ✅ |
| [`guides/owasp-cheatsheets/`](guides/owasp-cheatsheets/SOURCE.md) | All 127 OWASP Cheat Sheets | 📦 |
| [`guides/owasp-mastg/`](guides/owasp-mastg/SOURCE.md) | OWASP MASTG tests, techniques, knowledge, and best practices | 📦 |
| [`reporting/`](reporting/README.md) | Normalized severity scale and rule metadata (draft, awaiting agreement) | 🗺️ |
| [`reporting/compliance-mapping/`](reporting/compliance-mapping/README.md) | MASVS, ASVS 5.0, and 88 Prowler frameworks including PCI DSS 4.0, CIS, ISO 27001 | 📦 |
| [`templates/threat-models/`](templates/threat-models/README.md) | OWASP Threat Model Cookbook, Threagile and threatcl examples | 📦 |
| [`manuals/`](manuals/README.md) | Install, use, and triage manuals for 91 tools, with links to each tool's GitHub repository | ✅ |
| [`docs/research/`](docs/research/README.md) | Tool evaluations, including the [map of 96 open-source projects](docs/research/open-source-map.md) | ✅ |

### Act

| Directory | Contents | Status |
| :--- | :--- | :--- |
| [`skills/`](skills/README.md) | 51 AI agent skills in 10 security domains | ✅ |
| [`skills/trailofbits/`](skills/trailofbits/README.md) | 23 Claude Code plugins (38 skills): Semgrep rule creation, SARIF analysis, variant analysis, supply-chain risk | 📦 |
| [`playbooks/`](playbooks/README.md) | Leaked secrets, compromised dependencies, finding triage | 🗺️ |
| [`labs/`](labs/README.md) | Reproducible vulnerable-and-fixed exercises | 🗺️ |

## How the repository is organized

- **Every directory has a README** that says what belongs there, what is already in it, and its status.
- **Imported content stays in its own directory** with the upstream license and a `SOURCE.md` naming the project, commit, and any changes. All imports are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- **Research comes first.** A new scanner, policy pack, or imported rule set starts with a note in [`docs/research/`](docs/research/README.md).
- **One severity scale** across tools is defined in [reporting/severity-and-metadata.md](reporting/severity-and-metadata.md).
- **The order of work** is in the [roadmap](ROADMAP.md).

```text
devsecopsforall/
├── public/            Interactive DevSecOps roadmap published on GitHub Pages
├── rules/             All rule sets: Semgrep, YARA, secret patterns, nuclei, Falco
├── scanners/          Scanner wrappers, configuration, ZAP scripts
├── policies/          Policy-as-code: Kubernetes, CI/CD, Terraform, containers, supply chain
├── integrations/      CI templates, pre-commit, DefectDojo import (planned)
├── tools/             Standalone utilities (planned)
├── manuals/           How to install, use, and triage 91 tools
├── guides/            Review checklists, OWASP Cheat Sheets, OWASP MASTG
├── reporting/         Severity scale and compliance mappings
├── templates/         Threat model templates and examples
├── skills/            AI agent skills, including Trail of Bits plugins
├── playbooks/         Incident and triage procedures (planned)
├── labs/              Reproducible exercises (planned)
├── docs/research/     Tool evaluations and the open-source map
├── ROADMAP.md         What gets built next
└── THIRD_PARTY_NOTICES.md   Source and license of every import
```

## Contributing

A precise rule, a tested policy, a clearer manual, or a fixed link are all welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) and the README of the directory you are changing, include tests or examples that show the behavior, and record the source and license of anything you import. The [roadmap](ROADMAP.md) lists open work.

## Responsible use

> [!IMPORTANT]
> Use these tools only on systems you own or are authorized to assess. Never commit credentials, customer data, or unredacted scan results.

Report vulnerabilities in this repository privately, following the [security policy](SECURITY.md).

## License

Original material is under the [MIT License](LICENSE). Imported content keeps its own license — including GPL, AGPL-3.0, CC-BY-SA-4.0, DRL 1.1, and the Elastic License 2.0 in the directories that carry them; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), the [mobile rule notices](rules/semgrep/mobile/NOTICE.md), and the [skill notices](skills/THIRD_PARTY_NOTICES.md).

<div align="center">
  Maintained by <a href="https://github.com/1ega">@1ega</a> with contributions from the community.
</div>
