# OWASP Dependency-Check

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0  
**Notes:** Writes GitLab dependency scanning reports

[GitHub: dependency-check/DependencyCheck](https://github.com/dependency-check/DependencyCheck) · [Documentation](https://dependency-check.github.io/DependencyCheck)

## What it is for

NVD-based scanner, strongest for Java and .NET, with a GitLab report format.

Mature and audit-friendly, with a native GitLab format. It needs an NVD API key and a cached data directory, otherwise updates are very slow.

## Install

**Homebrew**

```bash
brew install dependency-check
```

**Container image**

```bash
docker pull owasp/dependency-check
```

## Use

**Scan and write all report formats**

```bash
dependency-check.sh --project "my-app" --scan . --format ALL --out reports/ --nvdApiKey "$NVD_API_KEY"
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
dependency-check:
  stage: test
  image:
    name: owasp/dependency-check:latest
    entrypoint: [""]
  script:
    - /usr/share/dependency-check/bin/dependency-check.sh
        --project "$CI_PROJECT_NAME" --scan .
        --format GITLAB --format SARIF --out reports/
        --nvdApiKey "$NVD_API_KEY" --failOnCVSS 9
  cache:
    paths: [/usr/share/dependency-check/data]   # mount or cache the NVD data
  artifacts:
    when: always
    paths: [reports/]
    reports:
      dependency_scanning: reports/dependency-check-gitlab.json
```

## Output and triage

By default it never fails; `--failOnCVSS 9` exits 15 when a CVSS score of 9 or higher is found. Request a free NVD API key and store it as a masked CI/CD variable.

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
- [retire.js](retire.md) — Finds JavaScript libraries with known vulnerabilities, including copies vendored into static files.
