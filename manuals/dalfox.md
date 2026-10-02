# Dalfox

**Area:** 7. Test what runs → Dynamic testing (DAST)  
**License:** MIT

[GitHub: hahwul/dalfox](https://github.com/hahwul/dalfox) · [Documentation](https://dalfox.hahwul.com/)

## What it is for

Fast scanner focused on reflected, stored, and DOM XSS.

Goes deeper on XSS than general scanners and verifies payloads. Feed it the endpoints from your OpenAPI spec.

## Install

**Homebrew or Snap**

```bash
brew install dalfox
# or
sudo snap install dalfox
```

## Use

**Scan a URL**

```bash
dalfox scan https://staging.example.com/search?q=test
```

## Output and triage

DefectDojo has no Dalfox parser; convert results to the Generic Findings Import format to track them there.

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
- [Burp Suite](burp.md) — Intercepting proxy and scanner for manual web and API testing.
