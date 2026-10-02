# slsa-verifier

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0  
**Notes:** Provenance from the SLSA GitHub generator and Google Cloud Build

[GitHub: slsa-framework/slsa-verifier](https://github.com/slsa-framework/slsa-verifier) · [Documentation](https://github.com/slsa-framework/slsa-verifier#readme)

## What it is for

Verifies SLSA provenance before you install or deploy an artifact.

Closes the loop: a release is only trusted if its provenance proves it was built from the expected repository and branch.

> [!WARNING]
> It does not verify provenance produced by GitLab CI or Bitbucket Pipelines.

## Install

**Go**

```bash
go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@v2.7.1
```

## Use

**Verify an artifact**

```bash
slsa-verifier verify-artifact my-app-linux-amd64 \
  --provenance-path my-app-linux-amd64.intoto.jsonl \
  --source-uri github.com/my-org/my-app
```

## Output and triage

Prints `PASSED: Verified SLSA provenance` on success.

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
- [witness](witness.md) — Wraps build steps and produces signed in-toto attestations.
- [sbomqs](sbomqs.md) — Scores SBOM quality and checks it against standards such as BSI and NTIA.
