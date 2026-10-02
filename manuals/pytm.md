# pytm

**Area:** 9. Run the program → Threat modeling  
**License:** MIT

[GitHub: OWASP/pytm](https://github.com/OWASP/pytm) · [Documentation](https://github.com/OWASP/pytm)

## What it is for

Threat model as Python code that generates diagrams and reports.

Suits teams that prefer code to diagrams. Needs Graphviz and PlantUML for diagrams.

## Install

**From source**

```bash
git clone https://github.com/OWASP/pytm && cd pytm
pip install -e .
```

## Use

**Generate a diagram and a report**

```bash
./tm.py --dfd | dot -Tpng -o dfd.png
./tm.py --report docs/basic_template.md > report.md
```

## Concepts to know

- STRIDE
- Data flow diagrams
- Trust boundaries
- Attack surface
- Threat model as code

## Related tools

- [OWASP Threat Dragon](threat-dragon.md) — Visual editor for data flow diagrams and STRIDE threats; can store models in GitLab.
- [Threagile](threagile.md) — Threat model as YAML with automatic risk rules and reports.
- [threatcl](threatcl.md) — Threat models in HCL with validation, diagrams, and a dashboard.
