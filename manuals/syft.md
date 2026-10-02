# syft

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0  
**Notes:** CycloneDX report for GitLab  
**Recommended first choice in this topic.**

[GitHub: anchore/syft](https://github.com/anchore/syft) · [Documentation](https://oss.anchore.com/docs/guides/sbom/getting-started/)

## What it is for

Generates CycloneDX or SPDX SBOMs from images and directories.

Fast, accurate, and covers dozens of ecosystems. Generate one SBOM per release and feed it to Grype, Dependency-Track, and GitLab.

## Install

**Install script**

```bash
curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin
```

## Use

**SBOM for an image**

```bash
syft my-app:latest -o cyclonedx-json=sbom.cdx.json
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
  image: alpine:3.20                 # the official image has no shell
  before_script:
    - apk add --no-cache curl
    - curl -sSfL https://get.anchore.io/syft | sh -s -- -b /usr/local/bin
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
