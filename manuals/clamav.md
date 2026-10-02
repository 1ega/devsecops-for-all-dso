# ClamAV

**Area:** 1. Protect your code → Malware and malicious code  
**License:** GPL-2.0

[GitHub: Cisco-Talos/clamav](https://github.com/Cisco-Talos/clamav) · [Documentation](https://docs.clamav.net/)

## What it is for

Open-source antivirus engine for files, archives, and uploads.

A simple last check on build artifacts, image filesystems, and user uploads, with signature updates from Cisco Talos.

## Install

**Homebrew or container**

```bash
brew install clamav
# or
docker pull clamav/clamav
```

## Use

**Update signatures, then scan recursively and list only infected files**

```bash
freshclam
clamscan -r -i path/to/scan
```

## Output and triage

`clamscan` exits 1 when it finds infected files. Signature-based detection misses targeted, custom malware; combine it with YARA and code review.

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
- [THOR Lite](thor-lite.md) — IOC and YARA-based compromise assessment scanner, free edition.
- [Claude Code security review](claude-security-review.md) — AI review of code changes for vulnerabilities and suspicious logic, as a GitHub Action or the /security-review command.
