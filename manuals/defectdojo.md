# DefectDojo

**Area:** 9. Run the program → Vulnerability management and release gates  
**License:** BSD-3-Clause  
**Recommended first choice in this topic.**

[GitHub: DefectDojo/django-DefectDojo](https://github.com/DefectDojo/django-DefectDojo) · [Documentation](https://docs.defectdojo.com/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/integrations/defectdojo)

## What it is for

Imports results from 200+ scanners, deduplicates them, and tracks them per product.

One place for every finding, with parsers for the GitLab report formats and every tool on this page. Reimport closes findings automatically when they disappear.

## Install

**Docker Compose**

```bash
git clone https://github.com/DefectDojo/django-DefectDojo
cd django-DefectDojo && docker compose up -d
docker compose logs initializer | grep "Admin password:"
```

## Use

**Import a SARIF report**

```bash
curl -X POST "$DD_URL/api/v2/reimport-scan/" \
  -H "Authorization: Token $DD_API_KEY" \
  -F scan_type="SARIF" -F file=@semgrep.sarif \
  -F product_name="my-service" -F engagement_name="CI" \
  -F auto_create_context=true
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
defectdojo-upload:
  stage: .post
  image: alpine:3.20
  before_script:
    - apk add --no-cache curl
  script:
    - for f in *.sarif; do
        curl -sf -X POST "$DD_URL/api/v2/reimport-scan/"
          -H "Authorization: Token $DD_API_KEY"
          -F scan_type="SARIF" -F "file=@$f" -F test_title="$f"
          -F product_name="$CI_PROJECT_PATH" -F engagement_name="$CI_DEFAULT_BRANCH"
          -F auto_create_context=true;
      done
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

## Output and triage

Use `reimport-scan` for recurring CI scans so fixed findings close automatically. Scan type names come from the parsers, for example "SARIF", "Semgrep JSON Report", "Gitleaks Scan", and "Trivy Scan".

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

- [Dependency-Track](dependency-track.md) — Continuously re-checks uploaded SBOMs against new vulnerability data.
- [secureCodeBox](securecodebox.md) — Runs scanners as Kubernetes jobs on a schedule and ships results to DefectDojo.
