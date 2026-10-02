# cdxgen

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0

[GitHub: cdxgen/cdxgen](https://github.com/cdxgen/cdxgen) · [Documentation](https://cdxgen.github.io/cdxgen)

## What it is for

CycloneDX generator from source code, with deep language support.

Builds richer SBOMs from source than image scanners can, including dependency trees and evidence. Good for polyglot repositories.

## Install

**npm or Homebrew**

```bash
npm install -g @cdxgen/cdxgen --ignore-scripts
# or
brew install cdxgen
```

## Use

**Recursive SBOM for a repository**

```bash
cdxgen -r -o bom.json .
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
cdxgen:
  stage: build
  image:
    name: ghcr.io/cdxgen/cdxgen:master
    entrypoint: [""]
  script:
    - cdxgen -r -o bom.json .
  artifacts:
    paths: [bom.json]
    reports:
      cyclonedx: bom.json
```

## Output and triage

The npm package was renamed from `@cyclonedx/cdxgen` to `@cdxgen/cdxgen`; update old install commands.

## Concepts to know

- Software supply chain
- SBOM: CycloneDX and SPDX
- Artifact repository
- Artifact signing
- Keyless signing with OIDC
- Provenance and SLSA levels
- Artifact integrity

## Related tools

- [syft](syft.md) — Generates CycloneDX or SPDX SBOMs from images and directories.
- [cosign](cosign.md) — Signs and verifies images and files; keyless with the GitLab job identity.
- [SLSA GitHub generator](slsa-github-generator.md) — Reusable workflows that produce SLSA Build Level 3 provenance on GitHub Actions.
- [slsa-verifier](slsa-verifier.md) — Verifies SLSA provenance before you install or deploy an artifact.
- [witness](witness.md) — Wraps build steps and produces signed in-toto attestations.
- [sbomqs](sbomqs.md) — Scores SBOM quality and checks it against standards such as BSI and NTIA.
