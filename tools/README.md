# Tools

Independent utilities with explicit inputs, outputs and validation.

| Tool | Purpose | Status |
| :--- | :--- | :--- |
| [dso](dso/README.md) | Repository scans, normalized finding gates, inventory, evidence and exception checks | Published |

## Suggested layout

```text
tools/
└── tool-name/
    ├── README.md
    ├── src/ or executable files
    ├── tests/              when applicable
    └── dependency manifest when applicable
```

The exact layout can match the language and size of the tool. Keep dependencies and generated files inside its directory where practical.

## Tool README checklist

- Purpose and intended audience
- Requirements and installation
- Commands and example input/output
- Required permissions and target scope
- Side effects, limitations, and cleanup
- Tests or other verification steps
- License information, if different terms are explicitly provided

Add a tool to the [root catalog](../README.md#whats-inside) only when its code and guide are available.

Published: [dso](dso/README.md) for private evidence/exception checks and [repository validation](validation/README.md). Repository scanner orchestration and a shared [MCP server](../mcp/dso/README.md) are available.
