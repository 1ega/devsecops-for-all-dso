# GuardDog

**Area:** 1. Protect your code → Malware and malicious code  
**License:** Apache-2.0  
**Recommended first choice in this topic.**

[GitHub: DataDog/guarddog](https://github.com/DataDog/guarddog) · [Documentation](https://github.com/DataDog/guarddog#readme)

## What it is for

Detects malicious PyPI, npm, Go, and GitHub Actions packages with source and metadata heuristics.

Looks for what vulnerability scanners ignore: install-time code execution, exfiltration, obfuscation, and typosquatted names. Check a package before you add it.

## Install

**pip, uvx, or container**

```bash
pip install guarddog
# or
uvx guarddog --help
# or
docker run --rm ghcr.io/datadog/guarddog --help
```

## Use

**Scan a package before adding it**

```bash
guarddog pypi scan requests
guarddog npm scan express
```

**Check every dependency in a requirements file**

```bash
guarddog pypi verify requirements.txt
```

## Output and triage

Each finding names the rule that matched, for example `exec-base64` or `code-execution`. Narrow or exclude rules with `--rules` and `--exclude-rules`.

## Concepts to know

- Malicious packages
- Typosquatting and dependency confusion
- Backdoors and logic bombs
- Obfuscated code
- Indicators of compromise (IOC)
- YARA rules

## Related tools

- [YARA-X](yara-x.md) — Pattern-matching rules for malware and suspicious files; the Rust successor to YARA.
- [ClamAV](clamav.md) — Open-source antivirus engine for files, archives, and uploads.
- [THOR Lite](thor-lite.md) — IOC and YARA-based compromise assessment scanner, free edition.
- [Claude Code security review](claude-security-review.md) — AI review of code changes for vulnerabilities and suspicious logic, as a GitHub Action or the /security-review command.
