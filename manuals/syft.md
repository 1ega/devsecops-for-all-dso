# syft

**Version reviewed:** 1.54.0 ([release](https://github.com/anchore/syft/releases/tag/v1.54.0)). Install and verify the matching release package before CI use.

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0  
**Notes:** CycloneDX report for GitLab  
**Recommended first choice in this topic.**

[GitHub: anchore/syft](https://github.com/anchore/syft) · [Documentation](https://oss.anchore.com/docs/guides/sbom/getting-started/)

## What it is for

Generates CycloneDX or SPDX SBOMs from images and directories.

Fast, accurate, and covers dozens of ecosystems. Generate one SBOM per release and feed it to Grype, Dependency-Track, and GitLab.

## Install

**Verified release package (Linux amd64)**

The checksum below was read from the official release metadata on 2026-10-02.
Use the matching release asset/checksum for another OS or architecture.
SHA256 pinning checks integrity; review upstream signatures/provenance before
trusting a new release.

```bash
set -eu
curl --fail --show-error --location https://github.com/anchore/syft/releases/download/v1.54.0/syft_1.54.0_linux_amd64.tar.gz -o syft.tar.gz
printf '%s  %s\n' '54a87372498168b2d033e876fd41fa4e8035b872699e525a57046e1f2f09c860' 'syft.tar.gz' | sha256sum --check -
tar -xzf syft.tar.gz syft
sudo install -m 0755 syft /usr/local/bin/syft
```

On macOS, `brew install syft` is a convenient alternative; verify its installed
version before using it with a pinned CI setup.

## Use

**SBOM for an image**

```bash
syft "$IMAGE_DIGEST" -o cyclonedx-json=sbom.cdx.json
```

**Two formats at once**

```bash
syft ./ -o spdx-json=sbom.spdx.json -o cyclonedx-json=sbom.cdx.json
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
sbom:
  stage: build
  image: ubuntu:24.04@sha256:a853f94d226358a79c740cfc7bce0c289748f3fe3488d921d038ccd752c61b60
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - |
      curl --fail --show-error --location https://github.com/anchore/syft/releases/download/v1.54.0/syft_1.54.0_linux_amd64.tar.gz -o syft.tar.gz
      printf '%s  %s\n' '54a87372498168b2d033e876fd41fa4e8035b872699e525a57046e1f2f09c860' 'syft.tar.gz' | sha256sum --check -
      tar -xzf syft.tar.gz syft
      install -m 0755 syft /usr/local/bin/syft
  script:
    - syft dir:. -o cyclonedx-json=gl-sbom.cdx.json
  artifacts:
    paths: [gl-sbom.cdx.json]
    reports:
      cyclonedx: gl-sbom.cdx.json
```

## Output and triage

Keep the SBOM with the release artifact. Score its completeness with sbomqs and scan it with Grype.

## Concepts to know

- Software supply chain
- SBOM: CycloneDX and SPDX
- Artifact repository
- Artifact signing
- Keyless signing with OIDC
- Provenance and SLSA levels
- Artifact integrity

## Related tools

- [cdxgen](cdxgen.md) — CycloneDX generator from source code, with deep language support.
- [cosign](cosign.md) — Signs and verifies images and files; keyless with the GitLab job identity.
- [SLSA GitHub generator](slsa-github-generator.md) — Reusable workflows that produce SLSA Build Level 3 provenance on GitHub Actions.
- [slsa-verifier](slsa-verifier.md) — Verifies SLSA provenance before you install or deploy an artifact.
- [witness](witness.md) — Wraps build steps and produces signed in-toto attestations.
- [sbomqs](sbomqs.md) — Scores SBOM quality and checks it against standards such as BSI and NTIA.

Generate the SBOM from the immutable deployed image digest, retain it with the
release and record generator/database context. Check that packages and licenses
for your stack are represented. An SBOM is inventory; pair it with vulnerability
scanning, approved-signer verification and the [finding lifecycle](../reporting/finding-lifecycle.md).
