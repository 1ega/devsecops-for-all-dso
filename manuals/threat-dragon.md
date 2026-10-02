# OWASP Threat Dragon

**Area:** 9. Run the program → Threat modeling  
**License:** Apache-2.0  
**Recommended first choice in this topic.**

[GitHub: OWASP/threat-dragon](https://github.com/OWASP/threat-dragon) · [Documentation](https://www.threatdragon.com/docs/) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/templates/threat-models)

## What it is for

Visual editor for data flow diagrams and STRIDE threats; can store models in GitLab.

The easiest way to start with a team: draw the system, and it suggests threats per element. Models are JSON files you can keep in the repository.

## Install

**Desktop app or container**

```bash
# desktop installers: github.com/OWASP/threat-dragon/releases
docker run -it --rm -p 8080:3000 -v $(pwd)/.env:/app/.env threatdragon/owasp-threat-dragon:stable
```

## Use

**Open the editor**

```bash
open http://localhost:8080/
```

## Output and triage

Reports are printed or saved as PDF from the model view.

## Concepts to know

- STRIDE
- Data flow diagrams
- Trust boundaries
- Attack surface
- Threat model as code

## Related tools

- [Threagile](threagile.md) — Threat model as YAML with automatic risk rules and reports.
- [pytm](pytm.md) — Threat model as Python code that generates diagrams and reports.
- [threatcl](threatcl.md) — Threat models in HCL with validation, diagrams, and a dashboard.
