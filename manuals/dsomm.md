# OWASP DSOMM

**Area:** 9. Run the program → People, standards, and maturity  
**License:** GPL-3.0  
**Recommended first choice in this topic.**

[GitHub: devsecopsmaturitymodel/DevSecOps-MaturityModel](https://github.com/devsecopsmaturitymodel/DevSecOps-MaturityModel) · [Documentation](https://dsomm.owasp.org/)

## What it is for

DevSecOps Maturity Model: activities by dimension and level, with a self-hosted assessment app.

Built for exactly this roadmap: it lists concrete DevSecOps activities per level, so you can mark what you have and plan the next step.

## Install

**Run the assessment app**

```bash
docker run --rm -p 8080:8080 wurstbrot/dsomm:latest
```

## Use

**Open it**

```bash
open http://localhost:8080/
```

## Concepts to know

- Security champion program
- Security awareness training
- Acceptable use policy
- Maturity levels
- Security requirements
- Metrics that matter

## Related tools

- [OWASP SAMM](samm.md) — Software Assurance Maturity Model covering governance, design, implementation, verification, and operations.
- [OWASP ASVS](asvs.md) — Verification requirements for web applications and APIs, in three levels.
- [OWASP MASVS](masvs.md) — Security requirements for mobile apps, with the MASTG test guide.
- [GoPhish](gophish.md) — Phishing simulation toolkit for security awareness campaigns.
