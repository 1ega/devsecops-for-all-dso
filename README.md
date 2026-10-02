<div align="center">
  <img src="assets/banner.svg" alt="DevSecOps for All — security belongs in every workflow" width="100%">
  <h1>DevSecOps for All</h1>
  <p><strong>Build securely. Find what matters. Share what works.</strong></p>
  <p>A growing security toolbox for developers, defenders, and ethical hackers.</p>
  <p><strong>320</strong> mobile rules &nbsp;·&nbsp; <strong>51</strong> AI skills &nbsp;·&nbsp; <strong>10</strong> skill domains &nbsp;·&nbsp; <strong>3</strong> Python checks</p>
  <p><a href="#get-started">Get started</a> &nbsp;·&nbsp; <a href="#explore-the-collection">Explore</a> &nbsp;·&nbsp; <a href="#repository-map">Repository map</a> &nbsp;·&nbsp; <a href="CONTRIBUTING.md">Contribute</a></p>
</div>

---

## Security belongs in the workflow

Security work is easier when the rules, guidance, and examples live together. **DevSecOps for All** collects reusable checks and hands-on knowledge in one place: run a scan, understand the result, and improve the code or system behind it.

The repository is growing. The rule packs, skills, and guides below are available now; the other directories are clearly marked as spaces for future contributions.

## Explore the collection

| | Start here | What you'll find |
| :--- | :--- | :--- |
| **🛡️ Scan code** | [Python rules](rules/README.md) · [Mobile rules](semgrep-rules/mobile_custom/README.md) | Semgrep patterns, examples, and explanations. |
| **🤖 Equip an AI agent** | [Skill catalog](skills/README.md) | 51 skills across AppSec, infrastructure, supply chain, AI security, and response. |
| **📚 Work through a review** | [Guides](guides/README.md) | A security review checklist and a pentest planning guide. |
| **🧰 Build a tool** | [Tools directory](tools/README.md) | A place for focused, documented DevSecOps utilities. |

<details>
<summary><strong>Mobile rule coverage</strong></summary>

| Platform | Rules | Includes |
| :--- | ---: | :--- |
| Android | 233 | Authentication, cryptography, networking, storage, and platform checks |
| iOS | 32 | Keychain, cryptography, networking, and platform checks |
| React Native / Expo | 32 | Configuration, storage, and network checks |
| Flutter / Dart | 23 | Code, cryptography, networking, and resilience checks |

See the [mobile rule pack](semgrep-rules/mobile_custom/README.md) for exact scope, limitations, tests, and upstream notices.

</details>

## Get started

Install [Semgrep](https://semgrep.dev/docs/getting-started/quickstart/) and run these commands from the repository root. Replace the example paths with your own project.

**Python — scan with the starter rules**

```bash
semgrep scan --metrics=off --config rules/ path/to/python-project
```

**Mobile — scan an Android, iOS, React Native, or Flutter project**

```bash
semgrep scan --metrics=off --config semgrep-rules/mobile_custom/rules/ path/to/mobile-project
```

**Building a rule? Run the tests**

```bash
semgrep test rules/
```

For mobile rule tests, follow the [pack's testing instructions](semgrep-rules/mobile_custom/README.md#testing). A finding is a lead for review; confirm the data flow and context before calling it a vulnerability.

**Want an AI workflow?** Start with [secure code review](skills/appsec-testing/secure-code-review/SKILL.md), [authorized pentest](skills/appsec-testing/authorized-pentest/SKILL.md), or [prompt injection defense](skills/ai-security/prompt-injection-defense/SKILL.md). The [skill catalog](skills/README.md) explains how to use the full collection.

## Repository map

```text
devsecopsforall/
├── rules/           Python Semgrep starter rules
├── semgrep-rules/   Larger rule packs, including mobile_custom/
├── skills/          AI security skills by domain
├── guides/          Practical review and planning advice
├── tools/           Independent utilities
├── detections/      Detection content
├── integrations/    CI templates, pre-commit, DefectDojo
├── scanners/        Third-party scanner configurations
├── labs/            Reproducible exercises
├── playbooks/       Operational response procedures
├── policies/        Policy-as-code packs by target
├── reporting/       Severity conventions, compliance mapping
├── templates/       Assessment and decision documents
├── docs/research/   Tool evaluation notes
├── ROADMAP.md       What gets built next
└── .github/         Issue, PR, and workflow templates
```

### Spaces to grow

These directories are **structure only** today. Each README explains what belongs there and lists research candidates; no tool or rule is presented as finished before it exists. The [roadmap](ROADMAP.md) sets the order in which they get filled.

| Explore | Explore |
| :--- | :--- |
| [Integrations](integrations/README.md) — GitHub Actions, GitLab CI, pre-commit, DefectDojo | [Policies](policies/README.md) — Terraform, Kubernetes, containers, CI/CD, cloud, supply chain |
| [Scanners](scanners/README.md) — gitleaks, osv-scanner, Trivy, ZAP, nuclei, MobSF | [Reporting](reporting/README.md) — severity scale, metadata, compliance mapping |
| [Tools](tools/README.md) — standalone utilities, starting with the `dso` CLI | [Templates](templates/README.md) — threat models, findings, decision records |
| [Playbooks](playbooks/README.md) — leaked secrets, compromised dependencies, triage | [Detections](detections/README.md) — Sigma, YARA, Falco, osquery |
| [Labs](labs/README.md) — isolated, reproducible exercises | [Research notes](docs/research/README.md) — tool evaluations behind each addition |

## Contribute

Good contributions can be a single precise rule, a safer example, clearer documentation, a useful skill, or a complete tool. Choose the relevant directory, include evidence that it works, and explain its limits.

1. Read [CONTRIBUTING.md](CONTRIBUTING.md), the README in your target directory, and the [roadmap](ROADMAP.md).
2. Add examples and tests where behavior can be verified; keep credentials and private data out.
3. Open a pull request with the purpose, verification steps, and any security implications.

## Responsible use

> [!IMPORTANT]
> Use security tools only on systems you own or are authorized to assess. Review their scope and permissions before running them. Never commit real credentials, sensitive scan output, or customer data.

Found a weakness in the repository or its tools? Follow the [security policy](SECURITY.md) instead of posting sensitive details in a public issue.

## License and credits

Original material is available under [MIT](LICENSE). Imported material keeps its original terms: see the [mobile rule notices](semgrep-rules/mobile_custom/NOTICE.md) and [skill notices](skills/THIRD_PARTY_NOTICES.md) for authorship and licenses.

---

<div align="center">
  <strong>Security is a team sport.</strong><br>
  Built and maintained by <a href="https://github.com/1ega">@1ega</a> with contributions from the community.
</div>
