# YARA-X

**Area:** 1. Protect your code → Malware and malicious code  
**License:** BSD-3-Clause

[GitHub: VirusTotal/yara-x](https://github.com/VirusTotal/yara-x) · [Documentation](https://virustotal.github.io/yara-x/) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/skills/trailofbits/yara-authoring)

## What it is for

Pattern-matching rules for malware and suspicious files; the Rust successor to YARA.

The standard language for describing malware. Run community or your own rules over repositories, build output, and image filesystems. Classic YARA (VirusTotal/yara) uses the same rules.

## Install

**Homebrew or Cargo**

```bash
brew install yara-x
# or
cargo install yara-x-cli
```

## Use

**Scan a directory with a rule file**

```bash
yr scan rules/malware.yar path/to/scan
```

## Output and triage

Start with curated community rule sets and tune them; broad rules produce many false positives on source code.

## Concepts to know

- Malicious packages
- Typosquatting and dependency confusion
- Backdoors and logic bombs
- Obfuscated code
- Indicators of compromise (IOC)
- YARA rules

## Related tools

- [GuardDog](guarddog.md) — Detects malicious PyPI, npm, Go, and GitHub Actions packages with source and metadata heuristics.
- [ClamAV](clamav.md) — Open-source antivirus engine for files, archives, and uploads.
- [THOR Lite](thor-lite.md) — IOC and YARA-based compromise assessment scanner, free edition.
- [Claude Code security review](claude-security-review.md) — AI review of code changes for vulnerabilities and suspicious logic, as a GitHub Action or the /security-review command.
