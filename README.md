<div align="center">
  <img src="assets/banner.svg" alt="DevSecOps for All — the security Swiss Army knife" width="100%">

  # DevSecOps for All

  ### The DevSecOps Swiss Army knife

  Practical security rules, AI skills, field guides, and a growing workspace for the tools that connect them.

  **320 mobile rules** · **3 Python starter rules** · **a growing library of security skills**

  [Open the toolbox](#the-toolbox) · [Start scanning](#start-here) · [Explore the roadmap](ROADMAP.md) · [Contribute](CONTRIBUTING.md)
</div>

<br>

<img align="right" width="43%" src="profile/assets/security-illustration.png" alt="Security engineer tracing a finding from code to a verified fix">

### 🧭 One kit, from signal to fix

Security work crosses code, pipelines, infrastructure, and operations. This repository brings the pieces together so a finding can lead to a clear next step.

- 🔎 **Find it:** Semgrep rules for Python and mobile applications.
- 🧠 **Understand it:** reusable AI skills and practical review guides.
- 🛠️ **Improve it:** planned scanner presets, policies, CI integrations, and reporting.
- 🧪 **Prove it:** tests, reproducible labs, and evidence-based playbooks as the toolbox grows.

The goal is simple: make useful security checks easy to discover, run, review, and improve.

<br clear="all">

---

<a id="the-toolbox"></a>

### 🧰 The toolbox

**Ready to use**

- **[Mobile Semgrep rules](semgrep-rules/mobile_custom/README.md)** — 320 checks for Android, iOS, React Native / Expo, and Flutter / Dart. Includes test cases, known limitations, and upstream license notices.
- **[Python starter rules](rules/README.md)** — three focused checks for shell execution, disabled TLS verification, and unsafe YAML loading, with match and non-match tests.
- **[AI security skills](skills/README.md)** — workflows across AppSec, AI security, supply chain, CI/CD, cloud, host hardening, and incident response.
- **[Field guides](guides/README.md)** — security review and pentest planning you can use alongside the rules.

**On the workbench**

- **[Scanner presets](scanners/README.md) + [manuals](manuals/README.md)** — planned configurations and practical instructions for external tools.
- **[Policies](policies/README.md) + [integrations](integrations/README.md)** — planned controls for infrastructure and delivery workflows.
- **[`dso` CLI](tools/dso/README.md) + [reporting](reporting/README.md)** — a planned entry point and common finding format; `dso` is design only today.
- **[Detections](detections/README.md), [playbooks](playbooks/README.md), and [labs](labs/README.md)** — space for operational content and reproducible exercises.
- **[Curated upstream material](THIRD_PARTY_NOTICES.md)** — new rule packs, skills, and references are being reviewed with their sources and licenses recorded.

The [roadmap](ROADMAP.md) tracks the order in which these areas become runnable. A directory or design document is not a released tool.

<a id="start-here"></a>

### 🚀 Start here

Install [Semgrep](https://semgrep.dev/docs/getting-started/quickstart/), then run from the repository root against a project you are authorized to assess.

**Scan Python**

```bash
semgrep scan --metrics=off --config rules/ path/to/python-project
```

**Scan a mobile app**

```bash
semgrep scan --metrics=off --config semgrep-rules/mobile_custom/rules/ path/to/mobile-project
```

Choose a single platform or category from the [mobile rule guide](semgrep-rules/mobile_custom/README.md) when you need a narrower scan. Rule authors can run `semgrep test rules/` for the Python starter pack; the mobile pack has its [own test instructions](semgrep-rules/mobile_custom/README.md#testing).

**Working with an AI agent?** Try [secure code review](skills/appsec-testing/secure-code-review/SKILL.md), [authorized pentest](skills/appsec-testing/authorized-pentest/SKILL.md), or [prompt injection defense](skills/ai-security/prompt-injection-defense/SKILL.md). Browse the [full skill catalog](skills/README.md) for more.

### 🗂️ Find your way around

- **Scan and evaluate:** [`rules/`](rules/README.md) · [`semgrep-rules/`](semgrep-rules/README.md) · [`scanners/`](scanners/README.md) · [`docs/research/`](docs/research/README.md)
- **Automate and enforce:** [`integrations/`](integrations/README.md) · [`policies/`](policies/README.md) · [`tools/`](tools/README.md) · [`reporting/`](reporting/README.md)
- **Learn and respond:** [`skills/`](skills/README.md) · [`guides/`](guides/README.md) · [`manuals/`](manuals/README.md) · [`playbooks/`](playbooks/README.md) · [`labs/`](labs/README.md)
- **Share reusable work:** [`templates/`](templates/README.md) · [`detections/`](detections/README.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md)

### 🤝 Build with us

Have a rule, skill, guide, or tool that makes a security task easier to repeat? Read the [contribution guide](CONTRIBUTING.md), choose the right directory, and include examples, tests where applicable, limitations, and source/license information. The [roadmap](ROADMAP.md) lists good starting points; [research notes](docs/research/README.md) record decisions behind new additions.

> [!IMPORTANT]
> Use security tools only on systems you own or are authorized to assess. Treat findings as leads for review, and keep credentials, customer data, and sensitive scan output out of the repository.

Found a vulnerability here? Use the [security policy](SECURITY.md) for private reporting.

### 📜 License and credits

Original material is under [MIT](LICENSE). Imported rules, skills, and reference material keep their own terms; see the [repository notices](THIRD_PARTY_NOTICES.md), [mobile rule notices](semgrep-rules/mobile_custom/NOTICE.md), and [skill notices](skills/THIRD_PARTY_NOTICES.md).

---

<div align="center">
  <strong>Build · Verify · Secure</strong><br>
  Maintained by <a href="https://github.com/1ega">@1ega</a> with contributions from the community.
</div>
