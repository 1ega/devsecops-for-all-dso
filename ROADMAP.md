# Roadmap

The order in which the empty directories get filled. Each item should start with a [research note](docs/research/README.md) and end with tested content and an updated README.

## Phase 0 — Foundation

- [ ] Run `semgrep --validate` and `semgrep --test` for `semgrep-rules/mobile_custom/` in CI; [rules.yml](.github/workflows/rules.yml) currently tests only `rules/`.
- [ ] Agree on [severity and metadata](reporting/severity-and-metadata.md).
- [ ] Fill missing metadata in the mobile pack: `cwe` is present in 106 of 255 rule files and `masvs` in 40.
- [ ] Add a Markdown link check to CI.
- [x] Survey open-source projects for each section — see the [open-source map](docs/research/open-source-map.md).
- [x] Import reusable upstream content with licenses and `SOURCE.md` files — see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- [ ] Run `semgrep --validate` and `semgrep --test` for the imported `elttam/` and `trailofbits/` packs in CI.

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
- [ ] [Policies](policies/README.md): tune the imported Kyverno and Gatekeeper libraries into a default pack; write Terraform, CI/CD, and cloud policies.
- [ ] [Trivy](scanners/trivy/README.md), [ZAP](scanners/zap/README.md), and [nuclei](scanners/nuclei/README.md) configurations.

## Phase 4 — Knowledge and operations

- [x] [Manuals](manuals/README.md) for 91 tools, with links to each tool's GitHub repository.
- [ ] Deepen the manuals of the tools marked "start here" with tuning and triage examples.
- [ ] [Compliance mapping](reporting/compliance-mapping/README.md): standards and Prowler cloud mappings are imported; map this repository's rules to MASVS, ASVS, and PCI DSS 4.0.
- [ ] [Playbooks](playbooks/README.md) for leaked secrets, compromised dependencies, and triage.
- [ ] [Threat model templates](templates/threat-models/README.md) for login, biometrics, payments, and deep links (examples are imported).
- [x] Import open-source [YARA rule sets](detections/yara/README.md).
- [ ] Tuned [detection](detections/README.md) packs of our own (YARA with fixtures, Sigma, Falco) and first [labs](labs/README.md).
