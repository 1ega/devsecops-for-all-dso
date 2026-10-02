# sbomqs

**Version reviewed:** v2.1.2 ([official release](https://github.com/interlynk-io/sbomqs/releases/tag/v2.1.2)); metadata checked 2026-10-02.

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0

[GitHub: interlynk-io/sbomqs](https://github.com/interlynk-io/sbomqs) · [Documentation](https://github.com/interlynk-io/sbomqs/tree/main/docs)

## What it is for

Scores SBOM quality and checks it against standards such as BSI and NTIA.

An SBOM with missing versions or suppliers is of little use. Gate releases on a minimum quality score.

## Install

**Homebrew or Go**

```bash
brew tap interlynk-io/interlynk && brew install sbomqs
# or
go install github.com/interlynk-io/sbomqs/v2@v2.1.2
```

## Use

**Score an SBOM**

```bash
sbomqs score sbom.cdx.json
sbomqs score sbom.cdx.json --json
```

## Output and triage

`score` does not fail on its own. Gate with jq in the job script; check the JSON field name for your version, because the docs show both `avg_score` and `sbom_quality_score`.

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
- [SLSA GitHub generator](slsa-github-generator.md) — Reusable workflows that produce SLSA Build Level 3 provenance on GitHub Actions.
- [slsa-verifier](slsa-verifier.md) — Verifies SLSA provenance before you install or deploy an artifact.
- [witness](witness.md) — Wraps build steps and produces signed in-toto attestations.
