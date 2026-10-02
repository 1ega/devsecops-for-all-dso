# Dependency-Track

**Area:** 9. Run the program → Vulnerability management and release gates  
**License:** Apache-2.0

[GitHub: DependencyTrack/dependency-track](https://github.com/DependencyTrack/dependency-track) · [Documentation](https://dependencytrack.github.io/docs/)

## What it is for

Continuously re-checks uploaded SBOMs against new vulnerability data.

A scan only tells you about today. Dependency-Track alerts you when a new CVE affects a release you shipped months ago.

> [!WARNING]
> The main branch is v5; v4 reaches end of life in December 2026. Plan new deployments on v5.

## Install

**Deploy with the official quickstart or Helm charts**

```bash
# https://dependencytrack.github.io/docs/ and github.com/DependencyTrack/helm-charts
```

## Use

**Upload an SBOM**

```bash
curl -X POST "$DT_URL/api/v1/bom" -H "X-Api-Key: $DT_API_KEY" \
  -F "autoCreate=true" -F "projectName=my-service" \
  -F "projectVersion=$CI_COMMIT_REF_NAME" -F "bom=@sbom.cdx.json"
```

## Output and triage

The API key needs the BOM_UPLOAD permission, plus project creation permissions for `autoCreate`.

## Concepts to know

- Vulnerability lifecycle
- CVSS and SSVC
- KEV catalog
- Prioritization
- Deployment and quality gates
- Risk acceptance with expiry
- Remediation SLAs
- Vulnerability disclosure program

## Related tools

- [DefectDojo](defectdojo.md) — Imports results from 200+ scanners, deduplicates them, and tracks them per product.
- [secureCodeBox](securecodebox.md) — Runs scanners as Kubernetes jobs on a schedule and ships results to DefectDojo.
