# witness

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0

[GitHub: in-toto/witness](https://github.com/in-toto/witness) · [Documentation](https://witness.dev)

## What it is for

Wraps build steps and produces signed in-toto attestations.

Captures evidence about how each step ran (environment, materials, products) and verifies the whole chain against a policy.

> [!WARNING]
> Its GitLab attestor documentation still relies on `CI_JOB_JWT`, which GitLab removed in 17.0. Test it on your GitLab version before relying on it.

## Install

**Install script**

```bash
bash <(curl -s https://raw.githubusercontent.com/in-toto/witness/main/install-witness.sh)
```

## Use

**Attest a build step**

```bash
witness run -s build -a environment -k buildkey.pem -o build-attestation.json -- make build
```

**Verify against a policy**

```bash
witness verify -p policy-signed.json -a build-attestation.json -k policypub.pem -f ./app
```

## Output and triage

`witness verify` exits 0 only when every attestation required by the policy is present and valid.

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
- [sbomqs](sbomqs.md) — Scores SBOM quality and checks it against standards such as BSI and NTIA.
