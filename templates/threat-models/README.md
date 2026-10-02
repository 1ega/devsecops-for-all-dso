# Threat models

STRIDE threat model templates for common features, so a team starts from known threats instead of a blank page. Each template lists the assets, trust boundaries, typical threats, and the controls and checks in this repository that address them.

Planned templates:

- Login and session handling
- Biometric and local authentication
- Payments and transfers
- Deep links and universal links
- Third-party SDK integration

Research candidates: [OWASP/threat-dragon](https://github.com/OWASP/threat-dragon) (diagrams), [OWASP/pytm](https://github.com/OWASP/pytm) (threat model as code), [Threagile/threagile](https://github.com/Threagile/threagile) (YAML model with automatic risks). Related skill: [threat-modeling](../../skills/appsec-testing/threat-modeling/SKILL.md).

Imported examples:

| Directory | Contents | License |
| :--- | :--- | :--- |
| [threat-model-cookbook](threat-model-cookbook/SOURCE.md) | OWASP collection of flow diagrams, attack trees, and a blank template | CC-BY-4.0 |
| [threagile](threagile/SOURCE.md) | Example and stub YAML models for Threagile | MIT |
| [threatcl](threatcl/SOURCE.md) | Example HCL models, including a reusable control library | MIT |

**Status:** Examples imported; templates for the features above are not published yet.
