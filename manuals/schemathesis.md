# Schemathesis

**Area:** 7. Test what runs → Dynamic testing (DAST)  
**License:** MIT  
**Notes:** Upstream GitLab CI guide

[GitHub: schemathesis/schemathesis](https://github.com/schemathesis/schemathesis) · [Documentation](https://schemathesis.readthedocs.io/en/stable/)

## What it is for

Property-based API tests generated from OpenAPI or GraphQL schemas.

Finds crashes, schema violations, and auth bypasses by generating thousands of valid and invalid requests from the spec you already have.

## Install

**uv or pip**

```bash
uv tool install schemathesis
# or
pip install schemathesis
```

## Use

**Test an API from its schema**

```bash
schemathesis run https://staging.example.com/openapi.json --report junit
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
schemathesis:
  stage: dast
  image:
    name: schemathesis/schemathesis:stable
    entrypoint: [""]
  script:
    - >-
      schemathesis run "$TARGET_URL/openapi.json"
      --header "Authorization: Bearer $API_TOKEN"
      --wait-for-schema 60 --report junit
      --report-junit-path schemathesis-report/junit.xml
  artifacts:
    when: always
    reports:
      junit: schemathesis-report/junit.xml
```

## Output and triage

Exit code 1 when a check fails, 2 for configuration or schema errors. The explicit
JUnit path avoids relying on a generated report filename. Use staging data and
protect reports containing request/response evidence. Schema fuzzing complements
the [authorization matrix](../guides/api-authorization.md); it cannot prove all
business access rules. See the [CLI reference](https://schemathesis.readthedocs.io/en/stable/reference/cli/).

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
- [nuclei](nuclei.md) — Template-driven checks for exposures, misconfigurations, and known CVEs.
- [RESTler](restler.md) — Stateful REST API fuzzer that learns dependencies between requests.
- [Dalfox](dalfox.md) — Fast scanner focused on reflected, stored, and DOM XSS.
- [Burp Suite](burp.md) — Intercepting proxy and scanner for manual web and API testing.
