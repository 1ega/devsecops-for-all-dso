# Grype

**Version reviewed:** v0.120.0 ([official release](https://github.com/anchore/grype/releases/tag/v0.120.0)); metadata checked 2026-10-02.

**Area:** 1. Protect your code → Dependency scanning (SCA)  
**License:** Apache-2.0

[GitHub: anchore/grype](https://github.com/anchore/grype) · [Documentation](https://oss.anchore.com/docs/)

**In this repository:** [SARIF scan wrapper and starter configuration](../scanners/grype/README.md).

## What it is for

Vulnerability matcher for directories, images, and SBOMs.

Pairs with syft: generate the SBOM once, then scan it with Grype at every stage without rebuilding.

## Install

**Verified release package (Linux amd64)**

The checksum below was read from the official release metadata on 2026-10-02.
Use the matching release asset/checksum for another OS or architecture.
SHA256 pinning checks integrity; review upstream signatures/provenance before
trusting a new release.

```bash
set -eu
curl --fail --show-error --location https://github.com/anchore/grype/releases/download/v0.120.0/grype_0.120.0_linux_amd64.tar.gz -o grype.tar.gz
printf '%s  %s\n' 'a5a1218dce63acdac152a6b3b5bb366e7267e36f4069848cf455543b3fa5700e' 'grype.tar.gz' | sha256sum --check -
tar -xzf grype.tar.gz grype
sudo install -m 0755 grype /usr/local/bin/grype
```

On macOS, `brew install grype` is a convenient alternative; verify its installed
version before using it with a pinned CI setup.

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
  image: ubuntu:24.04@sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - |
      curl --fail --show-error --location https://github.com/anchore/grype/releases/download/v0.120.0/grype_0.120.0_linux_amd64.tar.gz -o grype.tar.gz
      printf '%s  %s\n' 'a5a1218dce63acdac152a6b3b5bb366e7267e36f4069848cf455543b3fa5700e' 'grype.tar.gz' | sha256sum --check -
      tar -xzf grype.tar.gz grype
      install -m 0755 grype /usr/local/bin/grype
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
