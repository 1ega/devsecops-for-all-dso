# Falco runtime detection

This directory ships **16 original syscall rules**, a pinned Helm configuration,
metadata, exception examples and validation scripts. Start with the
[manual](../../manuals/falco.md) and [triage runbook](triage.md).

| Files | Purpose |
| :--- | :--- |
| [dso-runtime.yaml](dso-runtime.yaml) | Standalone macros and 16 rules; MIT |
| [rule-catalog.json](rule-catalog.json) | Stable IDs, ATT&CK references, ownership, limitations |
| [helm/values.yaml](helm/values.yaml) | Chart 9.2.0, Falco 0.45.0, pinned image/rules/plugin digests |
| [exceptions.example.yaml](exceptions.example.yaml) | Process/parent tuple override; inactive placeholder |
| [tests/](tests/README.md) | Contracts, native compiler and positive/negative smoke test |

Coverage: interactive and web-spawned shells, credential/token reads, runtime
sockets, temporary and memory-backed executables, package managers, discovery
tools, miner names, privilege helpers, ptrace, SSH/cron/systemd/account writes,
and security-log removal. Each catalog entry explains its limitations.
Keep the pinned upstream rules enabled. Process names and paths are heuristics.

```bash
bash rules/falco/validate.sh
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm upgrade --install falco falcosecurity/falco --version 9.2.0 \
  -n falco --create-namespace -f rules/falco/helm/values.yaml \
  --set-file 'customRules.dso-runtime\.yaml=rules/falco/dso-runtime.yaml'
```

The quotes preserve the dot in the rule filename. The manual includes rendering
and rollout verification. `rule_matching: all` prevents upstream matches hiding
local rules; measure CPU, drops and duplicate alerts. Artifact following is
disabled; review engine, chart, rules and plugin upgrades together.

**Validation:** structural checks and Helm rendering can run locally. Engine
compilation and syscall execution require Docker; see [test status](tests/README.md).
Deployment files do not prove production coverage or successful alert delivery.
