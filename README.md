<div align="center">
  <img src="assets/banner.svg" alt="DevSecOps for All — security belongs in every workflow" width="100%">

  # DevSecOps for All

  **Practical security tools for the people who build, ship, and run software.**

  [Explore tools](#tool-catalog) · [Semgrep rules](rules/README.md) · [AI skills](skills/README.md) · [Contribute](CONTRIBUTING.md) · [License](LICENSE)
</div>

---

## What is this?

**DevSecOps for All** is a home for practical DevSecOps tools, Semgrep rules, field guides, and AI skills that make secure delivery easier to practice. The catalog will grow as new material is tested and documented.

The aim is simple: make each tool easy to discover, run, review, and improve.

## Tool catalog

| Area | What's available | Status |
| :--- | :--- | :--- |
| 🛡️ Semgrep | [Python security rules](rules/README.md) and [mobile application rules](semgrep-rules/mobile_custom/README.md) | Available |
| 🤖 AI skills | [51 security skills in 10 categories](skills/README.md): AppSec testing, supply chain, CI/CD and IaC, secrets, Kubernetes, host and network hardening, AI security, detection and response, compliance | Available |
| 📚 Guides | [Security review checklist](guides/security-review.md) and [pentest planning](guides/pentest-planning.md) | Available |
| 🧰 Tools | [Independent utilities](tools/README.md) | Open for contributions |

Each future utility will have its own README with prerequisites, setup, examples, and limitations.

## Quick start

Run the included Semgrep rules against a Python project:

```bash
semgrep scan --config rules/ path/to/python-project
```

For Android, iOS, React Native, and Flutter projects, see the [mobile rule set](semgrep-rules/mobile_custom/README.md):

```bash
semgrep scan --metrics=off --config semgrep-rules/mobile_custom/rules/ path/to/mobile-project
```

Run the rule tests before changing a pattern:

```bash
semgrep test rules/
```

See [rule documentation](rules/README.md) for finding behavior and limitations. To use an AI skill, copy its directory into your agent's skills directory or provide its `SKILL.md` as instructions. Review the [scope and safety guidance](guides/pentest-planning.md) before any active assessment.

## Repository map

```text
devsecopsforall/
├── assets/          Visual identity
├── guides/          Practical checklists and planning advice
├── rules/           Semgrep rules with positive and negative examples
├── semgrep-rules/   Mobile rules with separate license and notices
├── skills/          Reusable AI agent instructions, grouped by category
├── tools/           Independent tools, one directory per tool
├── .github/         Contribution templates
├── CONTRIBUTING.md  How to add or improve a tool
└── SECURITY.md      How to report a vulnerability
```

## Add a tool

1. Read the [contribution guide](CONTRIBUTING.md).
2. Create `tools/<tool-name>/` with a README, source, and focused tests where applicable.
3. Document what the tool does, what it touches, and how to run it safely.
4. Open a pull request using the repository template.

See the [tool directory guide](tools/README.md) for the expected layout.

## Responsible use

Use security tools only on systems you own or are authorized to assess. Review a tool's scope and required permissions before running it. Never commit real credentials, sensitive scan output, or customer data.

Found a weakness in this repository or one of its tools? Follow the [security policy](SECURITY.md).

## License

Original material in this repository is available under the [MIT License](LICENSE). Third-party material keeps its own terms: the [mobile Semgrep rules](semgrep-rules/mobile_custom/NOTICE.md) include GPL-3.0 and other upstream licenses, while imported [AI skills](skills/THIRD_PARTY_NOTICES.md) include MIT and Apache-2.0 material. The root MIT license does not replace those notices.

---

<div align="center">
  Built for a more approachable, hands-on DevSecOps community.<br>
  Maintained by <a href="https://github.com/1ega">@1ega</a> · Contributions welcome.
</div>
