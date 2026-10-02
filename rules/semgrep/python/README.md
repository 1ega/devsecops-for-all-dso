# Semgrep rules

Three focused Python rules with nearby test cases:

| Rule | Detects | Caveat |
| :--- | :--- | :--- |
| `python-subprocess-shell-true` | `subprocess` calls with `shell=True` | Review whether untrusted input can reach the command. |
| `python-requests-verify-false` | `requests` calls disabling TLS verification | May be intentional in a controlled test environment. |
| `python-yaml-unsafe-load` | `yaml.unsafe_load` or `yaml.load` with an unsafe loader | Safe loading can still require schema validation. |

## Run

Install [Semgrep](https://semgrep.dev/docs/getting-started/quickstart/) and run from the repository root:

```bash
semgrep scan --config rules/semgrep/python/ path/to/python-project
semgrep test rules/semgrep/python/
```

These are review prompts, not proof of exploitability. Check whether the data is trusted and whether the flagged behavior is required. A clean scan does not establish that a codebase is secure.

When adding a rule, include at least one match and one non-match test. Explain the risk and an actionable alternative in its message.
