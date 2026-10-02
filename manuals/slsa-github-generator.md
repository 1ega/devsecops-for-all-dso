# SLSA GitHub generator

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0  
**Notes:** GitHub Actions only

[GitHub: slsa-framework/slsa-github-generator](https://github.com/slsa-framework/slsa-github-generator) · [Documentation](https://github.com/slsa-framework/slsa-github-generator#readme)

## What it is for

Reusable workflows that produce SLSA Build Level 3 provenance on GitHub Actions.

Provenance is generated in an isolated reusable workflow, so the build job cannot forge it. Consumers verify it with slsa-verifier.

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitHub Actions

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      hashes: ${{ steps.hash.outputs.hashes }}
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
      - run: make build
      - id: hash
        run: echo "hashes=$(sha256sum dist/* | base64 -w0)" >> "$GITHUB_OUTPUT"
  provenance:
    needs: [build]
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2.1.0
    with:
      base64-subjects: "${{ needs.build.outputs.hashes }}"
```

## Output and triage

Reusable workflows must be referenced by tag (for example `@v2.1.0`), not by SHA; that is how the verifier identifies the builder.

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
- [cdxgen](cdxgen.md) — CycloneDX generator from source code, with deep language support.
- [cosign](cosign.md) — Signs and verifies images and files; keyless with the GitLab job identity.
- [slsa-verifier](slsa-verifier.md) — Verifies SLSA provenance before you install or deploy an artifact.
- [witness](witness.md) — Wraps build steps and produces signed in-toto attestations.
- [sbomqs](sbomqs.md) — Scores SBOM quality and checks it against standards such as BSI and NTIA.
