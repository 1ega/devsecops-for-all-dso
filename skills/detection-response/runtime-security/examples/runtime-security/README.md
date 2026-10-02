# Runtime security examples

The maintained rule/deployment entry point is [rules/falco](../../../../../rules/falco/README.md).
`falco-custom-rules.yaml` links to its original rule pack; `falco-values.yaml`
uses the same pinned configuration. `falcosidekick-values.yaml` enables internal
HTTP routing with UI disabled; supply output credentials through an existing
Kubernetes Secret, following the [manual](../../../../../manuals/falco.md).

Run all commands from the repository root:

```bash
bash rules/falco/validate.sh
helm upgrade --install falco falcosecurity/falco --version 9.2.0 -n falco --create-namespace \
  -f rules/falco/helm/values.yaml \
  --set-file 'customRules.dso-runtime\.yaml=rules/falco/dso-runtime.yaml'
```

See [tests](../../../../../rules/falco/tests/README.md) for live validation.
The existing Kyverno bridge is an optional design example; automatic labeling
and response are not implemented by installing Falco or this chart.
