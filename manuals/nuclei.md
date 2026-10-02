# nuclei

**Area:** 7. Test what runs → Dynamic testing (DAST)  
**License:** MIT

[GitHub: projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) · [Documentation](https://docs.projectdiscovery.io/tools/nuclei/overview) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/scanners/nuclei)

## What it is for

Template-driven checks for exposures, misconfigurations, and known CVEs.

Thousands of community templates, and templates are simple YAML, so writing one for your own API takes minutes.

## Install

**Go**

```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
```

## Use

**Scan a target**

```bash
nuclei -target https://staging.example.com
```

**SARIF output**

```bash
nuclei -u https://staging.example.com -sarif-export nuclei.sarif
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
nuclei:
  stage: dast
  image:
    name: projectdiscovery/nuclei:latest
    entrypoint: [""]
  script:
    - nuclei -u "$TARGET_URL" -severity medium,high,critical -sarif-export nuclei.sarif
  artifacts:
    when: always
    paths: [nuclei.sarif]
```

## Output and triage

nuclei does not fail on findings by itself; gate on the report in a later job.

## Concepts to know

- OWASP Top 10
- Security headers: CSP, Referrer-Policy, Permissions-Policy
- XSS and CSRF
- SSRF
- API schema exposure
- Rate limits
- Fuzz testing

## Related tools

- [OWASP ZAP](zap.md) — Web and API scanner with ready baseline, full, and OpenAPI scan scripts.
- [Schemathesis](schemathesis.md) — Property-based API tests generated from OpenAPI or GraphQL schemas.
- [RESTler](restler.md) — Stateful REST API fuzzer that learns dependencies between requests.
- [Dalfox](dalfox.md) — Fast scanner focused on reflected, stored, and DOM XSS.
- [Burp Suite](burp.md) — Intercepting proxy and scanner for manual web and API testing.
