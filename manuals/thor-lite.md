# THOR Lite

**Area:** 1. Protect your code → Malware and malicious code  
**License:** Free for use, closed source (Nextron Systems)

[Documentation](https://www.nextron-systems.com/thor-lite/)

## What it is for

IOC and YARA-based compromise assessment scanner, free edition.

Ships thousands of curated YARA rules and IOCs from a threat-intelligence vendor. Useful for scanning unpacked image filesystems and hosts for known malware and hacktools.

> [!WARNING]
> Download requires registration, and the license file must be renewed periodically. It is not open source.

## Install

**Download from Nextron after registering**

```bash
# https://www.nextron-systems.com/thor-lite/
./thor-lite-linux-64 --help
```

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
- [Claude Code security review](claude-security-review.md) — AI review of code changes for vulnerabilities and suspicious logic, as a GitHub Action or the /security-review command.
