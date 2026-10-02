# Research: SMB security foundation

**Date:** 2026-10-02
**Target directory:** `baseline/`, `tools/dso/`, `integrations/`, `policies/cloud/`, `playbooks/`

## Goal

Give a small or medium company a starting control set it can own, evidence and review, plus a first automated path for code. The result must work without a commercial platform and keep private evidence out of public git.

## Decision

Use [NIST CSF 2.0's Small Business Quick Start](https://www.nist.gov/itl/smallbusinesscyber/nist-cybersecurity-framework-0) for program scope, [CIS IG1](https://www.cisecurity.org/controls/implementation-groups/ig1) and [CISA CPGs](https://www.cisa.gov/cybersecurity-performance-goals) for a practical initial set, and [NIST SSDF](https://csrc.nist.gov/pubs/sp/800/218/final) for software development. These are orientation sources; [`baseline/controls.json`](../../baseline/controls.json) is a small original catalog rather than a verbatim copy or a formal mapping.

Start with asset ownership and dated evidence. A scanner finding needs an asset, owner and remediation decision. Scanner output cannot confirm MFA, incident readiness, backup restoration or other operational controls, so [`dso`](../../tools/dso/README.md) checks owner-supplied evidence instead of claiming to verify it.

For the first automated path, use Gitleaks for current-tree secrets, OSV-Scanner for dependencies and Semgrep Community Edition with the registry's `p/default` ruleset for source code. Their images are pinned by digest in the [starter CI templates](../../integrations/README.md). Separate SARIF artifacts keep each raw tool result available while a common finding schema is designed. Semgrep's `auto` configuration is not used: it refuses to run with `--metrics off`.

## Open questions

- [ ] Cloud controls use owner-supplied evidence; no cloud account is connected or verified by this repository. The [evidence map](../../policies/cloud/evidence-map.md) lists what to collect until read-only collectors exist.
- [ ] The starter CI does not scan git history or gate SAST/SCA findings by severity.
- [ ] `p/default` comes from the Semgrep registry and OSV queries vulnerability data online. Organizations that need offline scans need a vetted local rule set and a data mirror.
- [ ] Every scanner needs a deliberately vulnerable fixture that proves it detects an expected issue and fails on tool errors. Trivy and Falco have them; Gitleaks, OSV-Scanner and Semgrep in the starter templates do not yet.
- [ ] DefectDojo ingestion, risk ownership and control-to-finding mapping remain future work.
