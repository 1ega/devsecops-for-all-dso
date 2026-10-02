# witness

**Version reviewed:** v0.12.0 ([official release](https://github.com/in-toto/witness/releases/tag/v0.12.0)); metadata checked 2026-10-02.

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0

[GitHub: in-toto/witness](https://github.com/in-toto/witness) · [Documentation](https://witness.dev)

## What it is for

Wraps build steps and produces signed in-toto attestations.

Captures evidence about how each step ran (environment, materials, products) and verifies the whole chain against a policy.

> [!WARNING]
> Its GitLab attestor documentation still relies on `CI_JOB_JWT`, which GitLab removed in 17.0. Test it on your GitLab version before relying on it.

## Install

**Verified release package (Linux amd64)**

The checksum below was read from the official release metadata on 2026-10-02.
Use the matching release asset/checksum for another OS or architecture.
SHA256 pinning checks integrity; review upstream signatures/provenance before
trusting a new release.

```bash
set -eu
curl --fail --show-error --location https://github.com/in-toto/witness/releases/download/v0.12.0/witness_0.12.0_linux_amd64.tar.gz -o witness.tar.gz
printf '%s  %s\n' '543d05898731fe5b9c176443ec596a0242bd27f0b327d73aff60f6f7398b7dd0' 'witness.tar.gz' | sha256sum --check -
tar -xzf witness.tar.gz witness
sudo install -m 0755 witness /usr/local/bin/witness
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
