# Tools

This directory will contain the independent tools in DevSecOps for All. There are no published tools here yet.

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

Add a tool to the [root catalog](../README.md#tool-catalog) only when its code and guide are available.
