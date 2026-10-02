# threatcl

**Area:** 9. Run the program → Threat modeling  
**License:** MIT

[GitHub: threatcl/threatcl](https://github.com/threatcl/threatcl) · [Documentation](https://threatcl.dev/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/templates/threat-models/threatcl)

## What it is for

Threat models in HCL with validation, diagrams, and a dashboard.

Feels natural to Terraform users and can validate models against invariants in CI.

## Install

**Homebrew**

```bash
brew install threatcl
```

## Use

**Validate models and build a dashboard**

```bash
threatcl validate models/*.hcl
threatcl dashboard -outdir dashboard models/*.hcl
```

## Output and triage

`threatcl validate -invariants=invariants.hcl` exits non-zero on error-severity violations, which makes it usable as a CI gate.

## Concepts to know

- STRIDE
- Data flow diagrams
- Trust boundaries
- Attack surface
- Threat model as code

## Related tools

- [OWASP Threat Dragon](threat-dragon.md) — Visual editor for data flow diagrams and STRIDE threats; can store models in GitLab.
- [Threagile](threagile.md) — Threat model as YAML with automatic risk rules and reports.
- [pytm](pytm.md) — Threat model as Python code that generates diagrams and reports.
