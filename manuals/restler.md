# RESTler

**Area:** 7. Test what runs → Dynamic testing (DAST)  
**License:** MIT

[GitHub: microsoft/restler-fuzzer](https://github.com/microsoft/restler-fuzzer) · [Documentation](https://github.com/microsoft/restler-fuzzer/tree/main/docs/user-guide)

## What it is for

Stateful REST API fuzzer that learns dependencies between requests.

Goes deeper than schema-based testing: it creates a resource, then uses its ID in later calls, finding bugs that only appear in sequences.

## Install

**Build locally (Python 3.12 and .NET 8 required)**

```bash
python ./build-restler.py --dest_dir <path-to-restler-bin>
```

## Use

**Compile the spec, smoke-test, then fuzz**

```bash
restler compile --api_spec openapi.json
restler test --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json
restler fuzz-lean --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json
```

## Output and triage

Bugs are written to `bug_buckets/bug_buckets.txt` under the results folder. Run it on schedule rather than on every merge request.

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
- [Dalfox](dalfox.md) — Fast scanner focused on reflected, stored, and DOM XSS.
- [Burp Suite](burp.md) — Intercepting proxy and scanner for manual web and API testing.
