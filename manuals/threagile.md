# Threagile

**Area:** 9. Run the program → Threat modeling  
**License:** MIT

[GitHub: Threagile/threagile](https://github.com/Threagile/threagile) · [Documentation](https://threagile.io) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/templates/threat-models/threagile)

## What it is for

Threat model as YAML with automatic risk rules and reports.

Lives in git and runs in CI, so the threat model is reviewed and updated with the code.

## Install

**Container image**

```bash
docker run --rm -it threagile/threagile --help
```

## Use

**Create an example model**

```bash
docker run --rm -it -v "$(pwd)":/app/work threagile/threagile --create-example-model --output /app/work
```

**Analyze a model**

```bash
docker run --rm -it -v "$(pwd)":/app/work threagile/threagile --model /app/work/threagile.yaml --output /app/work
```

## Output and triage

Produces a PDF report, risks as JSON and Excel, and data flow diagrams.

## Concepts to know

- STRIDE
- Data flow diagrams
- Trust boundaries
- Attack surface
- Threat model as code

## Related tools

- [OWASP Threat Dragon](threat-dragon.md) — Visual editor for data flow diagrams and STRIDE threats; can store models in GitLab.
- [pytm](pytm.md) — Threat model as Python code that generates diagrams and reports.
- [threatcl](threatcl.md) — Threat models in HCL with validation, diagrams, and a dashboard.
