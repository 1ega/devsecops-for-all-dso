# Contributing

Thanks for helping make DevSecOps tools easier to use. Improvements to documentation, examples, tests, and existing tools are welcome alongside new tools.

Semgrep rules should include match and non-match examples in `rules/`, and AI skills should include a focused description and workflow in `skills/<category>/<name>/SKILL.md`. Add new skills to the [skills catalog](skills/README.md), and record the source and license of imported skills in [THIRD_PARTY_NOTICES.md](skills/THIRD_PARTY_NOTICES.md).

## Before you start

- Check existing issues and pull requests to avoid duplicate work.
- For a new tool, open a feature request that describes the problem, intended users, and expected inputs and outputs.
- Keep tools focused. A tool should be usable and documented on its own.
- Only submit code and test data that you have the right to share.

## Add or change a tool

1. Put a new tool in `tools/<tool-name>/` using a short, lowercase, hyphenated name.
2. Include a README explaining the purpose, prerequisites, installation, usage, example output, permissions, limitations, and cleanup if the tool changes state.
3. Keep dependencies explicit and pinned where practical. Do not rely on credentials embedded in code or examples.
4. Add tests for meaningful behavior when the tool has executable code. Run the relevant checks and document anything you could not verify.
5. Add a direct link and accurate status to the catalog in the root README.
6. Open a pull request with a concise description, validation steps, and any security considerations.

The [tool directory guide](tools/README.md) includes a suggested layout and README checklist.

## Security and privacy

Never include real tokens, private keys, customer data, or unredacted findings in commits, issues, or pull requests. Use synthetic fixtures. If you discover a vulnerability, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

Tools that probe external systems must clearly describe their scope, permissions, rate limits, and effects. Examples should use local or explicitly authorized targets.

## Review expectations

Pull requests should be small enough to review, use clear names, and avoid unrelated changes. Maintainers may ask for clearer setup instructions, tests, or safer defaults before merging.
