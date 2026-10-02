# GoPhish

**Area:** 9. Run the program → People, standards, and maturity  
**License:** MIT

[GitHub: gophish/gophish](https://github.com/gophish/gophish) · [Documentation](https://getgophish.com/documentation/)

## What it is for

Phishing simulation toolkit for security awareness campaigns.

Measures how many people click and how many report, which is the awareness metric that matters. Run it from a dedicated, isolated account and domain.

> [!WARNING]
> Agree on scope, legal approval, and communication with HR before any campaign.

## Install

**Release binary or container**

```bash
# binaries: github.com/gophish/gophish/releases
docker run -it -p 3333:3333 -p 8080:80 gophish/gophish
```

## Use

**Open the admin UI and log in with the password printed in the log**

```bash
open https://localhost:3333
```

## Output and triage

Track click rate and report rate per campaign; the report rate should rise over time.

## Concepts to know

- Security champion program
- Security awareness training
- Acceptable use policy
- Maturity levels
- Security requirements
- Metrics that matter

## Related tools

- [OWASP DSOMM](dsomm.md) — DevSecOps Maturity Model: activities by dimension and level, with a self-hosted assessment app.
- [OWASP SAMM](samm.md) — Software Assurance Maturity Model covering governance, design, implementation, verification, and operations.
- [OWASP ASVS](asvs.md) — Verification requirements for web applications and APIs, in three levels.
- [OWASP MASVS](masvs.md) — Security requirements for mobile apps, with the MASTG test guide.
