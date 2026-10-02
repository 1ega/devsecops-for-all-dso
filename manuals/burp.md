# Burp Suite

**Area:** 7. Test what runs → Dynamic testing (DAST)  
**License:** Commercial; free Community Edition

[Documentation](https://portswigger.net/burp/documentation)

## What it is for

Intercepting proxy and scanner for manual web and API testing.

The standard tool for manual testing and verifying scanner findings. The Professional edition adds the automated scanner and extensions such as an MCP server for AI-assisted testing.

## Install

**Download**

```bash
# https://portswigger.net/burp/communitydownload
```

## Output and triage

Use it to confirm or dismiss findings from automated DAST before they reach developers.

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
- [Schemathesis](schemathesis.md) — Property-based API tests generated from OpenAPI or GraphQL schemas.
- [RESTler](restler.md) — Stateful REST API fuzzer that learns dependencies between requests.
- [Dalfox](dalfox.md) — Fast scanner focused on reflected, stored, and DOM XSS.
