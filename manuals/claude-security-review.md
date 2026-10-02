# Claude Code security review

**Area:** 1. Protect your code → Malware and malicious code  
**License:** MIT

[GitHub: anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) · [Documentation](https://github.com/anthropics/claude-code-security-review#readme) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/skills)

## What it is for

AI review of code changes for vulnerabilities and suspicious logic, as a GitHub Action or the /security-review command.

An AI reviewer reads intent, so it can flag hidden callbacks, credential harvesting, or time bombs that pattern rules miss. Pair it with Semgrep, as a malicious-code scan built on Claude Code does.

> [!WARNING]
> Results depend on the model and can include false positives or misses; keep a human in the loop for anything it marks as malicious.

## Use

**In Claude Code, review pending changes**

```bash
/security-review
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitHub Actions

```yaml
name: Security review
on: [pull_request]
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
        with:
          fetch-depth: 2
      - uses: anthropics/claude-code-security-review@main   # pin to a commit SHA
        with:
          comment-pr: true
          claude-api-key: ${{ secrets.CLAUDE_API_KEY }}
```

## Output and triage

Comments land on the pull request. The API key must be enabled for both the Claude API and Claude Code.

## Concepts to know

- Malicious packages
- Typosquatting and dependency confusion
- Backdoors and logic bombs
- Obfuscated code
- Indicators of compromise (IOC)
- YARA rules

## Related tools

- [GuardDog](guarddog.md) — Detects malicious PyPI, npm, Go, and GitHub Actions packages with source and metadata heuristics.
- [YARA-X](yara-x.md) — Pattern-matching rules for malware and suspicious files; the Rust successor to YARA.
- [ClamAV](clamav.md) — Open-source antivirus engine for files, archives, and uploads.
- [THOR Lite](thor-lite.md) — IOC and YARA-based compromise assessment scanner, free edition.
