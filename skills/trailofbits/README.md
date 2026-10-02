# Trail of Bits skills

Security-focused Claude Code plugins imported from [trailofbits/skills](https://github.com/trailofbits/skills) under CC-BY-SA-4.0. Each directory is a complete plugin (`.claude-plugin/plugin.json`, skills, and where present agents, commands, and scripts). See [SOURCE.md](SOURCE.md) for the commit and what was left out.

| Plugin | Use it for |
| :--- | :--- |
| [agentic-actions-auditor](agentic-actions-auditor/README.md) | Audits GitHub Actions workflows for security vulnerabilities in AI agent integrations (Claude Code Action, Gemini CLI, OpenAI Codex, GitHub AI Inference) |
| [audit-context-building](audit-context-building/README.md) | Understand a codebase before looking for bugs in it. Reads it function by function, records what each one assumes and depends on, and saves the write-ups to files instead of filling up the conversation |
| [burpsuite-project-parser](burpsuite-project-parser/README.md) | Search and extract data from Burp Suite project files (.burp) for security analysis |
| [c-review](c-review/README.md) | Comprehensive C/C++ security code review, with coverage verified against a parse of the source |
| [constant-time-analysis](constant-time-analysis/README.md) | Detect compiler-induced timing side-channels in cryptographic code |
| [differential-review](differential-review/README.md) | Security-focused differential review of code changes with git history analysis and blast radius estimation |
| [firebase-apk-scanner](firebase-apk-scanner/README.md) | Scan Android APKs for Firebase security misconfigurations including open databases, storage buckets, authentication issues, and exposed cloud functions |
| [fp-check](fp-check/README.md) | Systematic false positive verification for security bug analysis with mandatory gate reviews |
| [insecure-defaults](insecure-defaults/README.md) | Detects insecure default configurations including hardcoded credentials, fallback secrets, weak authentication defaults, and dangerous values in production |
| [open-sourcing](open-sourcing/README.md) | Prepares a repository for public open-source release: secrets-history hygiene, license selection, documentation and CI readiness checks, and language-specific packaging and release guidance |
| [post-patch-validation](post-patch-validation/README.md) | Validates security patches against the reported bug, root-cause variants, and surrounding behavior. Returns reproducible failures to repair and validation gaps, with pinned inputs and saved evidence. Bundles a validate-patch dynamic workflow for Claude Code |
| [rust-review](rust-review/README.md) | Comprehensive Rust security code review with specialized bug-finding agents covering the safe/unsafe boundary, memory safety in unsafe blocks, concurrency, panic-induced DoS, recursion-induced stack overflow, FFI, and async runtime hazards |
| [semgrep-rule-creator](semgrep-rule-creator/README.md) | Create custom Semgrep rules for detecting bug patterns and security vulnerabilities |
| [semgrep-rule-variant-creator](semgrep-rule-variant-creator/README.md) | Creates language variants of existing Semgrep rules with proper applicability analysis and test-driven validation |
| [sharp-edges](sharp-edges/README.md) | Identify error-prone APIs, dangerous configurations, and footgun designs that enable security mistakes |
| [spec-to-code-compliance](spec-to-code-compliance/README.md) | Check code against the documentation that specifies it: one agent per requirement, divergences refuted before they are reported, evidence cited to the line |
| [static-analysis](static-analysis/README.md) | Static analysis toolkit with CodeQL, Semgrep, and SARIF parsing for security vulnerability detection |
| [supply-chain-risk-auditor](supply-chain-risk-auditor/README.md) | Audit a project's npm, PyPI, and Go dependencies for supply-chain risk: version-matched advisories for direct dependencies and the full lockfile tree, abandoned upstreams, npm publisher concentration, and install scripts |
| [testing-handbook-skills](testing-handbook-skills/README.md) | Skills from the Trail of Bits Application Security Testing Handbook (appsec.guide) |
| [variant-analysis](variant-analysis/README.md) | Find similar vulnerabilities and bugs across codebases using pattern-based analysis |
| [vulnerability-triage-brocards](vulnerability-triage-brocards/README.md) | Principled framework for triaging vulnerability reports using 7 brocards (rules of thumb). Evaluates incoming CVEs, bug bounty submissions, and security findings against structured dismissal/acceptance criteria before escalating to deeper analysis |
| [yara-authoring](yara-authoring/README.md) | YARA-X detection rule authoring with linting and quality analysis |
| [zeroize-audit](zeroize-audit/README.md) | Detects missing or compiler-optimized zeroization of sensitive data with assembly and control-flow analysis |

Install a plugin in Claude Code with `/plugin install <path-to-plugin>` or copy its `skills/` directory into your agent's skills folder. Read bundled scripts before running them.
