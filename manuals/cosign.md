# cosign

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0  
**Notes:** Keyless signing with id_tokens  
**Recommended first choice in this topic.**

[GitHub: sigstore/cosign](https://github.com/sigstore/cosign) · [Documentation](https://docs.sigstore.dev/cosign/signing/overview/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/supply-chain/sigstore-policy-controller)

## What it is for

Signs and verifies images and files; keyless with the GitLab job identity.

Keyless signing ties each signature to the exact GitLab project and branch that built the image, with no key to store or rotate.

**Version covered:** 3.1.3; install the verified upstream release/package.

## Install

**Homebrew or Alpine**

```bash
brew install cosign
# in CI
apk add --no-cache cosign
```

## Use

**Verify an image signed by a GitLab pipeline**

```bash
cosign verify "$IMAGE" \
  --certificate-identity "https://gitlab.com/my-group/my-project//.gitlab-ci.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://gitlab.com"
```

## CI example

Use a dedicated protected release runner with verified Cosign 3.1.3 installed
and registry authentication configured. The build must provide `IMAGE_DIGEST`
as the full immutable image reference, not just a tag. No Docker-in-Docker or
local `docker inspect` is needed for signing.

```yaml
sign-image:
  stage: deploy
  tags: [protected-release]
  id_tokens:
    SIGSTORE_ID_TOKEN:
      aud: sigstore
  script:
    - test -n "$IMAGE_DIGEST"
    - cosign sign --yes --identity-token "$SIGSTORE_ID_TOKEN" "$IMAGE_DIGEST"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH && $CI_COMMIT_REF_PROTECTED == "true"
```

Keep shell tracing off and restrict runner/process/log access. Match the actual
certificate issuer and exact signing identity at verification/deploy time. Test
an unsigned image, wrong identity and wrong digest are rejected. Public keyless
signing publishes transparency information; assess private artifact naming
and use an approved Sigstore setup when needed. Signing without verification
by an approved identity does not form a release gate.

## Output and triage

Always sign by digest, not by tag. Enforce signatures at deploy with the Sigstore policy-controller or Kyverno `verifyImages`.

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
- [SLSA GitHub generator](slsa-github-generator.md) — Reusable workflows that produce SLSA Build Level 3 provenance on GitHub Actions.
- [slsa-verifier](slsa-verifier.md) — Verifies SLSA provenance before you install or deploy an artifact.
- [witness](witness.md) — Wraps build steps and produces signed in-toto attestations.
- [sbomqs](sbomqs.md) — Scores SBOM quality and checks it against standards such as BSI and NTIA.
