# SMB security baseline

This baseline covers the organization, cloud, infrastructure, delivery pipeline,
applications, and recovery. It is a starting checklist for a small or medium
company, not a claim of certification or complete protection.

## Use it

1. Copy `assets.example.csv` to a private inventory. Record every production
   service, cloud account, repository, and the person responsible for it. Do not
   put credentials or sensitive architecture details in this repository. Run
   `python3 tools/dso/dso.py inventory --input <assets.csv>` to check required fields,
   owners and duplicate IDs.
2. Copy `assessment.example.json` to a private assessment file. For each control,
   record `implemented`, `partial`, `missing`, or `not_applicable`, an owner,
   review date, and a link to evidence. `not_applicable` needs a reason.
3. Run `python3 tools/dso/dso.py assess --input <assessment.json>` from the repository
   root. The command checks completeness and evidence dates, then prints gaps.
4. Review missing and stale controls monthly and after major architecture changes.
   The assessment `as_of` date must be within seven days of the run so an old
   snapshot cannot appear current.

`controls.json` is the canonical control catalog. IDs are stable; change the
description or implementation guidance without renaming an ID. `tier: core`
marks the initial baseline. `tier: extended` applies when the technology exists.
Controls are outcomes, not tool endorsements. A scanner result alone is not
proof that a control is implemented in production.

## Evidence rules

- Keep evidence in the company's controlled storage, not in public git.
- Link to a dated ticket, export, configuration review, restore test, or alert
  test. Avoid uploading raw logs, secrets, or personal data.
- A control is `implemented` only when an owner and current evidence exist.
- Review intervals are in days. The checker marks older evidence as stale.
- Assessment data is an assertion by the owner. The checker validates its shape
  and freshness; it cannot independently verify a cloud or identity account.

## Reference framework

- [NIST CSF 2.0 Small Business Quick Start](https://www.nist.gov/itl/smallbusinesscyber/nist-cybersecurity-framework-0)
- [CIS Controls Implementation Group 1](https://www.cisecurity.org/controls/implementation-groups/ig1)
- [CISA Cross-Sector Cybersecurity Performance Goals](https://www.cisa.gov/cybersecurity-performance-goals)
- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final)

The `reference` values in the catalog are orientation links, not a formal
control-by-control compliance mapping.
