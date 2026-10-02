# Protect the pipeline and its runners

Separate untrusted pull-request checks from protected release/deployment jobs.
Start tokens at read-only; grant write/OIDC only to the specific protected job.
Use immutable action SHAs, image digests, include commits and pinned packages.
Review their updates and scanner database freshness.

| Control | Verification |
| :--- | :--- |
| Branch/release protection | Test direct-push denial, required review/checks and bypass list |
| Untrusted workflow input | Pass titles/branches via quoted environment variables; never interpolate them into shell code |
| Trigger boundary | No privileged checkout/execution of fork code under `pull_request_target` or equivalent |
| Runners | Disposable untrusted runners with no production secrets or persistent privileged caches |
| Secrets/OIDC | Exact trusted repo/project, branch/environment and audience; short-lived credentials |
| Artifacts/caches | Treat PR artifacts as untrusted; promote the tested digest, not a mutable tag |
| Gates | Tool failures and missing reports fail; findings follow the documented policy |
| Reporting | Private artifacts, minimum retention, no credential contents or shell tracing |

Docker daemon access grants substantial runner-host control even when source
mounts are read-only. Restrict GitLab Docker runners and never share production
runners with untrusted MRs. Protect CI config, dependency locks and policy files
through your normal review ownership settings.

Run [zizmor](../manuals/zizmor.md)/[actionlint](../manuals/actionlint.md) for GitHub
and [poutine](../manuals/poutine.md) for supported pipeline formats. Inspect
organization settings separately; static workflow checks cannot prove them.
Record a synthetic secret finding, a scanner error and a successful clean job
before enabling required checks. Use [starter templates](../integrations/README.md).

Source: [GitHub secure use](https://docs.github.com/en/actions/reference/security/secure-use)
and [OIDC](https://docs.github.com/en/actions/concepts/security/openid-connect).
