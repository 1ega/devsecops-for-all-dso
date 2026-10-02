<div align="center">
  <img src="assets/banner.svg" alt="DevSecOps for All — the security Swiss Army knife" width="100%">

  # DevSecOps for All

  ### The DevSecOps Swiss Army knife

</div>

DevSecOps for All collects security checks, policies, detection rules, standards, and manuals in one place, so a team can scan its code, cloud accounts, and clusters, enforce controls, hunt for malware, and know what to do with each finding.

> 🗺️ **[Explore the interactive DevSecOps roadmap →](https://1ega.github.io/devsecopsforall/)**
>
> Browse 10 security areas, 29 topics, and 95 tools, with installation steps, usage examples, full manuals, and links to 32 company baseline controls.

**[Quick start](#quick-start)** · **[Find by task](#find-by-task)** · **[What's inside](#whats-inside)** · **[How the repository is organized](#how-the-repository-is-organized)** · **[Roadmap](ROADMAP.md)** · **[Contributing](#contributing)**

## Quick start

Clone the repository to use its rules and configurations locally:

```bash
git clone https://github.com/1ega/devsecopsforall.git
cd devsecopsforall
```

Install the scanner you need separately. These examples use [Gitleaks](manuals/gitleaks.md#install) and [Semgrep](manuals/semgrep.md#install):

```bash
# Find secrets in a project's current files
gitleaks dir --redact=100 \
  --config rules/secrets/gitleaks-default/gitleaks.toml ../your-project

# Check Python code with the three starter rules
semgrep scan --metrics=off --error \
  --config rules/semgrep/python/ ../your-project
```

Replace `../your-project` with the directory you want to check. Both examples return exit code `1` when they find a match. Review the findings using the [triage playbook](playbooks/vulnerability-triage.md); for exposed credentials, follow the [leaked secret playbook](playbooks/leaked-secret.md).

For a company-wide rollout, start with the [SMB guide](guides/smb-security.md) and [security baseline](baseline/README.md).

## Find by task

| Task | Start here |
| :--- | :--- |
| Find secrets | [Gitleaks manual](manuals/gitleaks.md) · [Secret patterns](rules/secrets/secrets-patterns-db/SOURCE.md) |
| Review source code | [Semgrep rule packs](rules/semgrep/README.md) · [Code review checklist](guides/security-review.md) |
| Review a mobile app | [Mobile rules](rules/semgrep/mobile/README.md) · [OWASP MASTG](guides/owasp-mastg/SOURCE.md) |
| Check dependencies and images | [Grype](scanners/grype/README.md) · [Trivy](scanners/trivy/README.md) |
| Add security checks to CI | [GitHub Actions](integrations/github-actions/README.md) · [GitLab CI](integrations/gitlab-ci/README.md) · [pre-commit](integrations/pre-commit/README.md) |
| Check infrastructure code | [Terraform / conftest policies](policies/terraform/README.md) · [Trivy IaC config](scanners/trivy/config.yaml) |
| Harden Kubernetes | [Starter policies](policies/kubernetes/starter/README.md) · [Kyverno and Gatekeeper libraries](policies/kubernetes/README.md) |
| Audit cloud and SaaS accounts | [Prowler](scanners/prowler/README.md) · [SCuBA](manuals/scuba.md) |
| Test web apps and APIs | [ZAP manual](manuals/zap.md) · [API authorization tests](guides/api-authorization.md) |
| Detect malware or runtime threats | [YARA rules](rules/yara/README.md) · [Falco rules](rules/falco/README.md) |
| Handle findings and incidents | [Response playbooks](playbooks/README.md) · [OWASP Cheat Sheets](guides/owasp-cheatsheets/SOURCE.md) |
| Test backup recovery | [Restic manual](manuals/restic.md) · [Restore drill](playbooks/restore-drill.md) |
| Work with security standards | [ASVS, MASVS and Prowler frameworks](reporting/compliance-mapping/README.md) |
| Model threats | [Templates and examples](templates/threat-models/README.md) |
| Use security skills with an AI agent | [Skill catalog](skills/README.md) · [Trail of Bits plugins](skills/trailofbits/README.md) |

## What's inside

- [`rules/`](rules/README.md) — Semgrep, YARA, secret patterns, nuclei templates and Falco rules.
- [`scanners/`](scanners/README.md) — scanner configurations, Grype/Prowler/Trivy wrappers and ZAP scripts.
- [`policies/`](policies/README.md) — Kubernetes, Terraform, CI/CD, container and supply chain policies.
- [`integrations/`](integrations/README.md) — GitHub Actions, GitLab CI and pre-commit templates.
- [`baseline/`](baseline/README.md) and [`tools/dso/`](tools/dso/README.md) — company controls, inventory templates and evidence checks.
- [`manuals/`](manuals/README.md) and [`guides/`](guides/README.md) — tool setup, usage, review checklists and OWASP references.
- [`playbooks/`](playbooks/README.md) and [`reporting/`](reporting/README.md) — incident procedures, finding records, severity conventions and compliance references.
- [`templates/`](templates/README.md) — threat model templates and worked examples.
- [`skills/`](skills/README.md) — instructions for AI coding agents, including imported Trail of Bits plugins.
- [`docs/research/`](docs/research/README.md) — tool evaluations and implementation notes.

## How the repository is organized

Imported packs live in separate directories with their upstream license and a `SOURCE.md` recording the source commit and local changes. Collections assembled from several upstreams, the [mobile Semgrep rules](rules/semgrep/mobile/NOTICE.md) and the imported [AI skills](skills/THIRD_PARTY_NOTICES.md), record each source in a notice file instead. The [third-party notices](THIRD_PARTY_NOTICES.md) list the imports.

Check the component's README for its requirements, status and validation scope. Some directories contain reference material or plans: DefectDojo ingestion, cloud evidence collectors, automatic reporting adapters and [labs](labs/README.md) are still planned. The [roadmap](ROADMAP.md) tracks that work; the [review record](docs/research/smb-operational-gaps.md) describes what has been checked so far.

## Contributing

For bugs and questions, open an [issue](https://github.com/1ega/devsecopsforall/issues). To contribute rules, policies, examples or documentation, read [CONTRIBUTING.md](CONTRIBUTING.md). It covers tests, import requirements and where to put changes. The [validation guide](tools/validation/README.md) lists the repository checks.

Maintained by [@1ega](https://github.com/1ega).

## Security

Use the tools on systems you own or have permission to assess. Keep credentials and unredacted findings out of public commits and issues. Report vulnerabilities in this repository privately through [SECURITY.md](SECURITY.md).

## License

Original material is under the [MIT License](LICENSE). Imported content retains its upstream license; check the license in the relevant directory and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before reusing it. Additional notices cover the [mobile rules](rules/semgrep/mobile/NOTICE.md) and [AI skills](skills/THIRD_PARTY_NOTICES.md).
