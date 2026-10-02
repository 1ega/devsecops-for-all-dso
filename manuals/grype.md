# Grype

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0

[GitHub: anchore/grype](https://github.com/anchore/grype) · [Documentation](https://oss.anchore.com/docs/)

**In this repository:** [SARIF scan wrapper and starter configuration](../scanners/grype/README.md).

## What it is for

Vulnerability matcher for directories, images, and SBOMs.

Pairs with syft: generate the SBOM once, then scan it with Grype at every stage without rebuilding.

## Install

**Install script**

```bash
curl -sSfL https://get.anchore.io/grype | sudo sh -s -- -b /usr/local/bin
```

## Use

**Scan a directory or an SBOM**

```bash
grype ./my-project
grype sbom:./sbom.json
```

**SARIF output, fail on high**

```bash
grype dir:. -o sarif --file grype.sarif --fail-on high
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
grype:
  stage: test
  image: alpine:3.20                # the official image has no shell
  before_script:
    - apk add --no-cache curl
    - curl -sSfL https://get.anchore.io/grype | sh -s -- -b /usr/local/bin
  script:
    - grype dir:. -o sarif --file grype.sarif --fail-on high
  artifacts:
    when: always
    paths: [grype.sarif]
```

## Output and triage

`--fail-on` returns exit code 2 when a match is at or above the given severity.

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
- [OWASP Dependency-Check](dependency-check.md) — NVD-based scanner, strongest for Java and .NET, with a GitLab report format.
- [retire.js](retire.md) — Finds JavaScript libraries with known vulnerabilities, including copies vendored into static files.
