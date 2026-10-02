# Trivy (filesystem)

**Version covered:** 0.75.0. [Local configs and wrapper](../scanners/trivy/README.md).

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0  
**Notes:** GitLab report templates included

[GitHub: aquasecurity/trivy](https://github.com/aquasecurity/trivy) · [Documentation](https://trivy.dev/docs/latest/) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/scanners/trivy)

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

**Verified Linux amd64 release**

```bash
set -eu
curl --fail --show-error --location https://github.com/aquasecurity/trivy/releases/download/v0.75.0/trivy_0.75.0_Linux-64bit.tar.gz -o trivy.tar.gz
printf '%s  %s\n' 'c6e65abddb348e25f10549df887045629cf28cc72453cd1c63acb717316b3f3f' 'trivy.tar.gz' | sha256sum --check -
tar -xzf trivy.tar.gz trivy
sudo install -m 0755 trivy /usr/local/bin/trivy
```

This checksum comes from official release metadata reviewed on 2026-10-02.
Choose the matching package/checksum for another OS or architecture. Review
release provenance when adopting a new version.

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
    name: aquasec/trivy:0.75.0@sha256:af6acf9a6b85dfe389a1941505c0ce9efef52a4719635e1a962f022a3d855daa        # pin by digest
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

## Tuning and acceptance

Use immutable image references and a current database/check bundle. Keep unfixed
findings visible; accept risk only with asset scope, owner and expiry. Confirm
ecosystem/config-parser coverage and skipped files. Test a known positive and
negative fixture using [the local tests](../scanners/trivy/tests/README.md), retain
private reports, and distinguish tool failures from finding exit codes.
