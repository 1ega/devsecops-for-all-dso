# Supply chain

Controls that make releases traceable and tamper-evident: an SBOM for every release, signed images and artifacts, signature verification at deploy, SLSA provenance, and detection of malicious or typosquatted packages.

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| syft | [anchore/syft](https://github.com/anchore/syft) | SBOM generation (CycloneDX, SPDX) |
| cosign | [sigstore/cosign](https://github.com/sigstore/cosign) | Signing and attestations |
| SLSA GitHub generator | [slsa-framework/slsa-github-generator](https://github.com/slsa-framework/slsa-github-generator) | Provenance for GitHub Actions builds |
| GUAC | [guacsec/guac](https://github.com/guacsec/guac) | Graph of dependencies and attestations |
| Dependency-Track | [DependencyTrack/dependency-track](https://github.com/DependencyTrack/dependency-track) | Continuous SBOM monitoring |

Related skills: [supply-chain](../../skills/supply-chain/supply-chain/SKILL.md), [sbom-supply-chain](../../skills/supply-chain/sbom-supply-chain/SKILL.md). Response to a compromised dependency belongs in [playbooks](../../playbooks/README.md).

**Status:** Structure only; no policies are published yet.
