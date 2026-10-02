# Contributing

Thanks for helping make DevSecOps tools easier to use. Improvements to documentation, examples, tests, and existing tools are welcome alongside new tools.

Rules should include match and non-match examples next to the rule in [`rules/`](rules/README.md), and AI skills should include a focused description and workflow in `skills/<category>/<name>/SKILL.md`. Add new skills to the [skills catalog](skills/README.md), and record the source and license of imported skills in [THIRD_PARTY_NOTICES.md](skills/THIRD_PARTY_NOTICES.md).

Use the directory README for the kind of contribution you are making: [`rules/`](rules/README.md) for Semgrep, YARA, secret, nuclei, and Falco rules, [`policies/`](policies/README.md) for policy-as-code, [`integrations/`](integrations/README.md) for CI/CD recipes, [`playbooks/`](playbooks/README.md) for response procedures, [`templates/`](templates/README.md) for reusable documents, [`labs/`](labs/README.md) for exercises, and [`reporting/`](reporting/README.md) for finding formats and reporting tools, [`scanners/`](scanners/README.md) for third-party scanner configurations, and [`manuals/`](manuals/README.md) for tool manuals. Planned work is listed in the [roadmap](ROADMAP.md); record tool evaluations in [`docs/research/`](docs/research/README.md) before adding a new scanner or imported rule set.

## Before you start

- Check existing issues and pull requests to avoid duplicate work.
- For a new tool, open a feature request that describes the problem, intended users, and expected inputs and outputs.
- Keep tools focused. A tool should be usable and documented on its own.
- Only submit code and test data that you have the right to share.
- When importing content from another project, keep its license file, add a `SOURCE.md` with the upstream commit and any changes, and list the directory in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Do not import content from repositories without a license.

## Add or change a tool

1. Put a new tool in `tools/<tool-name>/` using a short, lowercase, hyphenated name.
2. Include a README explaining the purpose, prerequisites, installation, usage, example output, permissions, limitations, and cleanup if the tool changes state.
3. Keep dependencies explicit and pinned where practical. Do not rely on credentials embedded in code or examples.
4. Add tests for meaningful behavior when the tool has executable code. Run the relevant checks and document anything you could not verify.
5. Add a direct link and accurate status to the catalog in the root README.
6. Open a pull request with a concise description, validation steps, and any security considerations.

The [tool directory guide](tools/README.md) includes a suggested layout and README checklist.

## Add a scanner configuration

Start with a [research note](docs/research/README.md). The scanner must write SARIF or another format DefectDojo can import, so its results fit the [finding lifecycle](reporting/finding-lifecycle.md). Pin the tool by image digest or exact package version, record it in [tools/versions.json](tools/versions.json), and add a synthetic fixture that shows one match and one clean run.

## Security and privacy

Never include real tokens, private keys, customer data, or unredacted findings in commits, issues, or pull requests. Use synthetic fixtures. If you discover a vulnerability, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

Tools that probe external systems must clearly describe their scope, permissions, rate limits, and effects. Examples should use local or explicitly authorized targets.

## Review expectations

Pull requests should be small enough to review, use clear names, and avoid unrelated changes. Maintainers may ask for clearer setup instructions, tests, or safer defaults before merging.

Every change reaches `main` through a pull request. The `validate` job of the [repository validation](tools/validation/README.md) workflow must pass, and pull requests are squash-merged.
