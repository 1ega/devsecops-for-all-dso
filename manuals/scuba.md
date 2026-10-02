# CISA SCuBA: Microsoft 365 and Google Workspace posture

**Versions reviewed:** ScubaGear 1.8.0; ScubaGoggles 1.0.1.
[ScubaGear](https://github.com/cisagov/ScubaGear) ·
[ScubaGoggles](https://github.com/cisagov/ScubaGoggles).
Review each upstream repository's license/NOTICE; neither is copied here.

SCuBA provides secure configuration baselines and assessment tools for business
SaaS. This fills a gap that cloud infrastructure and code scanners do not cover.
Use ScubaGear for Microsoft 365 and ScubaGoggles for Google Workspace.

## Microsoft 365

Download ScubaGear release 1.8.0 and follow its prerequisite/module-install
instructions on supported PowerShell. Review required permissions per product,
use a dedicated assessment identity and handle consent through the tenant's
normal administrator process. After installing the reviewed module:

```powershell
Import-Module ScubaGear
Invoke-SCuBA -ProductNames *
```

Select only licensed/in-scope products for the tenant; retain reports privately.
Module installation alone does not grant the tool the necessary read access.

## Google Workspace

Use ScubaGoggles release 1.0.1 and its installation/authentication instructions.
Review required APIs, scopes, admin permissions and authorization before
assessment. Keep OAuth/client material in controlled storage; remove assessment
access when no longer needed. Execute the release's documented assessment
command and retain configuration/rule-version context with the report.

## Triage and retest

Assign the identity/SaaS owner to findings. Review MFA/admin separation, external
sharing, OAuth applications, forwarding, audit availability and retention.
Record failures, unsupported checks and license-dependent policies separately;
an unsupported check is not a pass. Stage changes with a recovery administrator
and test user, review business effects, then re-assess and record evidence for
`SAAS-01` and identity/logging controls. Review SPF/DKIM/DMARC, registrar ownership
and device management separately; a tenant score is not complete company coverage.
