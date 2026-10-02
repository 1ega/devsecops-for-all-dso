# Online roadmap synchronization audit

Reviewed 2026-10-02 against the [live map](https://1ega.github.io/devsecopsforall/)
and repository commit `4876c17`. The live `index.html`, `app.js` and `data.js`
matched the original local `public/` files. Pages last published the site at
`2999932`; the subsequent repository/manual update did not change those files.

| Observation | Correction |
| :--- | :--- |
| Live catalog: nine areas, 20 topics, 91 tools; repository: 95 manuals | Add Restic, osquery, Wazuh and CISA SCuBA |
| Company controls missing dedicated entry points | Add company ownership/vendor/data review, workforce identity, SaaS/email, endpoints, recovery and external DNS/TLS/exposure topics |
| Logging, response and API authorization absent from the topic map | Add guides, private-evidence acceptance steps and baseline control mappings |
| Tool cards duplicated old commands after manuals changed | Generate install/run/CI/results from all manuals; preserve IDs and saved browser adoption keys |
| Old Falco setup omitted local rules; ZAP suppressed errors; Cosign ignored OIDC token; versions and Semgrep paths were stale | Publish the corrected manual recipes through generated cards |
| `ROADMAP.md` described a separate future site and unimplemented work already present | Link the published site; record current content and remaining acceptance separately |
| Pages trigger only watched `public/` and its workflow | Watch manuals, catalog and baseline; fail stale/manual/control/resource checks before publishing |

The [published kit run](https://github.com/1ega/devsecopsforall/actions/runs/37031734420/job/110919961139)
passed repository and 22 Python tests, then failed before Falco rule compilation:
the CLI `load_plugins=[]` override was interpreted as a plugin named `[]`.
The updated harness removes that CLI override and retains the image's bundled
container plugin, which supplies `container.id`; disabling all plugins would
break the rules. Re-running the current `validate.sh` locally compiled both rule
files with Falco 0.45.0 (aarch64). The [test record](../../rules/falco/tests/README.md)
reports 16/16 positive rules and no negative alerts on a Docker Desktop Linux VM,
with the host `uname` guard bypassed; rule-specific non-match scenarios remain
unautomated. Confirm the next remote CI run. Runtime smoke in the earlier remote
run was skipped. [Semgrep CI](https://github.com/1ega/devsecopsforall/actions/runs/37031112656)
passed for the original three Python rules, not for every imported pack.

The updated source map has ten areas, 29 topics, 95 tools and all 32 baseline
controls. The [generator](../../tools/roadmap/README.md) rejects omitted manuals,
unmapped controls, duplicate/orphan topics, missing resources and copied/stale
instructions. Regression tests cover source drift, omissions, command preservation
and escaped text/unsafe links. The site displays acceptance checks and repository
validation limits; a browser adoption marker is not provider-verified evidence.

Remaining delivery work is explicit in [ROADMAP.md](../../ROADMAP.md): native
runtime acceptance/routing, broader imported-rule and scanner fixtures, normalized
finding gates/DefectDojo lifecycle, cluster/signature and real application tests,
cloud/log collectors and company recovery/access exercises. Coverage in this map
means an entry point exists, not that those controls are deployed.

These are local changes for review. The live site updates after they are pushed
and the publishing workflow succeeds.
