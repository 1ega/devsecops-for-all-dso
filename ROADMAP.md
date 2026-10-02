# Roadmap

The order in which the empty directories get filled. Each item should start with a [research note](docs/research/README.md) and end with tested content and an updated README.

## Phase 0 — Foundation

- [ ] Run `semgrep --validate` and `semgrep --test` for `semgrep-rules/mobile_custom/` in CI; [rules.yml](.github/workflows/rules.yml) currently tests only `rules/`.
- [ ] Agree on [severity and metadata](reporting/severity-and-metadata.md).
- [ ] Fill missing metadata in the mobile pack: `cwe` is present in 106 of 255 rule files and `masvs` in 40.
- [ ] Add a Markdown link check to CI.

## Phase 1 — One way in

- [ ] [GitHub Actions](integrations/github-actions/README.md) reusable workflow and [GitLab CI](integrations/gitlab-ci/README.md) template.
- [ ] [Semgrep profiles](semgrep-rules/profiles/README.md): `ci-blocking`, `pr-diff`, `audit`.
- [ ] [pre-commit](integrations/pre-commit/README.md) hooks.
- [ ] [DefectDojo](integrations/defectdojo/README.md) import.
- [ ] [dso](tools/dso/README.md) command-line entry point.

## Phase 2 — Complete mobile coverage

- [ ] Mobile secret patterns in [gitleaks](scanners/gitleaks/README.md).
- [ ] Mobile lockfiles in [osv-scanner](scanners/osv-scanner/README.md).
- [ ] Built artifact analysis with [MobSF](scanners/mobsf/README.md).
- [ ] Release build configuration rules in [mobile_custom](semgrep-rules/mobile_custom/README.md): network security config, R8, signing, Expo EAS, Flutter obfuscation.

## Phase 3 — Backend and infrastructure

- [ ] Backend Semgrep packs in [semgrep-rules](semgrep-rules/README.md).
- [ ] [Policies](policies/README.md): Terraform, Kubernetes, containers, CI/CD, cloud, supply chain.
- [ ] [Trivy](scanners/trivy/README.md), [ZAP](scanners/zap/README.md), and [nuclei](scanners/nuclei/README.md) configurations.

## Phase 4 — Knowledge and operations

- [ ] [Compliance mapping](reporting/compliance-mapping/README.md) to MASVS, ASVS, PCI DSS 4.0, and CIS.
- [ ] [Playbooks](playbooks/README.md) for leaked secrets, compromised dependencies, and triage.
- [ ] [Threat model templates](templates/threat-models/README.md).
- [ ] First [detection](detections/README.md) packs and [labs](labs/README.md).
