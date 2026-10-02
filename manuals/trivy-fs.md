# Trivy (filesystem)

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0  
**Notes:** GitLab report templates included

[GitHub: aquasecurity/trivy](https://github.com/aquasecurity/trivy) · [Documentation](https://trivy.dev/docs/latest/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/scanners/trivy)

## What it is for

One scanner for dependencies, secrets, and misconfiguration in a source tree.

Reads mobile lockfiles too (Gradle, pubspec.lock, Podfile.lock, Package.resolved) and ships templates that produce GitLab reports. One tool can cover dependencies, containers, and IaC.

> [!WARNING]
> In March 2026 trivy-action, setup-trivy, and Trivy images on Docker Hub were reported compromised. Pin the image by digest and verify its signature.

## Install

**Homebrew**

```bash
brew install trivy
```

**Install script**

```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin
```

## Use

**Scan dependencies, secrets, and misconfiguration**

```bash
trivy fs --scanners vuln,secret,misconfig .
```

**SARIF output**

```bash
trivy fs --format sarif -o trivy.sarif .
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
trivy-fs:
  stage: test
  image:
    name: aquasec/trivy:latest        # pin by digest
    entrypoint: [""]
  variables:
    TRIVY_NO_PROGRESS: "true"
    TRIVY_CACHE_DIR: .trivycache/
  script:
    - trivy fs --scanners misconfig,vuln --exit-code 0
        --format template --template "@/contrib/gitlab-codequality.tpl"
        -o gl-codeclimate-fs.json .
  cache:
    paths: [.trivycache/]
  artifacts:
    reports:
      codequality: gl-codeclimate-fs.json
```

## Output and triage

Trivy exits 0 even when it finds issues; add `--exit-code 1 --severity CRITICAL` to gate. Import JSON into DefectDojo as "Trivy Scan".

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
- [Grype](grype.md) — Vulnerability matcher for directories, images, and SBOMs.
- [OWASP Dependency-Check](dependency-check.md) — NVD-based scanner, strongest for Java and .NET, with a GitLab report format.
- [retire.js](retire.md) — Finds JavaScript libraries with known vulnerabilities, including copies vendored into static files.
