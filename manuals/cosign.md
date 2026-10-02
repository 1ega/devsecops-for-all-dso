# cosign

**Area:** 5. Trust your artifacts → SBOM, signing, and provenance  
**License:** Apache-2.0  
**Notes:** Keyless signing with id_tokens  
**Recommended first choice in this topic.**

[GitHub: sigstore/cosign](https://github.com/sigstore/cosign) · [Documentation](https://docs.sigstore.dev/cosign/signing/overview/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/supply-chain/sigstore-policy-controller)

## What it is for

Signs and verifies images and files; keyless with the GitLab job identity.

Keyless signing ties each signature to the exact GitLab project and branch that built the image, with no key to store or rotate.

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

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
sign-image:
  stage: deploy
  image: docker:27
  services: [docker:27-dind]
  id_tokens:
    SIGSTORE_ID_TOKEN:
      aud: sigstore
  variables:
    COSIGN_YES: "true"
  before_script:
    - apk add --no-cache cosign
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - IMAGE_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA")
    - cosign sign "$IMAGE_DIGEST"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

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
