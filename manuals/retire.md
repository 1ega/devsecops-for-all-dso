# retire.js

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0

[GitHub: RetireJS/retire.js](https://github.com/RetireJS/retire.js) · [Documentation](https://github.com/RetireJS/retire.js#readme)

## What it is for

Finds JavaScript libraries with known vulnerabilities, including copies vendored into static files.

Catches jQuery, Angular, and other libraries copied into `static/` folders, which lockfile scanners never see.

## Install

**npm**

```bash
npm install -g retire
```

## Use

**Scan the current project**

```bash
retire
```

**CycloneDX SBOM output**

```bash
retire --outputformat cyclonedx
```

## Output and triage

Exits with code 13 when it finds vulnerabilities; override with `--exitwith 0`.

## Concepts to know

- CVE, CPE, and NVD
- Known exploited vulnerabilities (KEV)
- Reachability analysis
- Lockfiles
- Dependency confusion
- Typosquatting
- End-of-life software

## Related tools

- [osv-scanner](osv-scanner.md) — Matches lockfiles against Google's OSV database, with offline mode.
- [Trivy (filesystem)](trivy-fs.md) — One scanner for dependencies, secrets, and misconfiguration in a source tree.
- [Grype](grype.md) — Vulnerability matcher for directories, images, and SBOMs.
- [OWASP Dependency-Check](dependency-check.md) — NVD-based scanner, strongest for Java and .NET, with a GitLab report format.
