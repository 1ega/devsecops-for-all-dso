# osv-scanner

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0  
**Recommended first choice in this topic.**

[GitHub: google/osv-scanner](https://github.com/google/osv-scanner) · [Documentation](https://google.github.io/osv-scanner) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/scanners/osv-scanner)

## What it is for

Matches lockfiles against Google's OSV database, with offline mode.

Free, fast, and precise: OSV data maps vulnerabilities to exact package versions, which keeps false positives low. Reads Gradle, npm, pip, Go, Cargo, and pub lockfiles.

## Install

**Homebrew or Go**

```bash
brew install osv-scanner
# or
go install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest
```

**Container image**

```bash
docker pull ghcr.io/google/osv-scanner:latest
```

## Use

**Scan a project recursively**

```bash
osv-scanner scan source -r .
```

**SARIF output**

```bash
osv-scanner scan source -r --format sarif --output-file osv.sarif .
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
osv-scanner:
  stage: test
  image:
    name: ghcr.io/google/osv-scanner:latest
    entrypoint: [""]
  script:
    - /osv-scanner scan source -r --format sarif --output-file osv.sarif .
  artifacts:
    when: always
    paths: [osv.sarif]
  allow_failure:
    exit_codes: [128]          # no lockfiles found
```

## Output and triage

Exit code 1 when vulnerabilities are found, 128 when no packages were found (common in repositories without lockfiles). Check CocoaPods and Swift Package Manager support in the docs before relying on it for iOS.

## Concepts to know

- CVE, CPE, and NVD
- Known exploited vulnerabilities (KEV)
- Reachability analysis
- Lockfiles
- Dependency confusion
- Typosquatting
- End-of-life software

## Related tools

- [Trivy (filesystem)](trivy-fs.md) — One scanner for dependencies, secrets, and misconfiguration in a source tree.
- [Grype](grype.md) — Vulnerability matcher for directories, images, and SBOMs.
- [OWASP Dependency-Check](dependency-check.md) — NVD-based scanner, strongest for Java and .NET, with a GitLab report format.
- [retire.js](retire.md) — Finds JavaScript libraries with known vulnerabilities, including copies vendored into static files.
