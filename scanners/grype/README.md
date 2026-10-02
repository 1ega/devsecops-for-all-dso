# Grype vulnerability scanning

**Status:** Repository integration. The scanner and vulnerability database are provided by [Anchore](https://github.com/anchore/grype); this directory contains our invocation and policy starting point.

Grype matches known vulnerabilities in a filesystem, container image, or [Syft](https://github.com/anchore/syft) SBOM. Start with the [full manual](../../manuals/grype.md), then use this wrapper when you need the same SARIF output and severity gate locally or in CI.

## Run

Install and pin an approved Grype release for your environment. From the repository root:

```bash
# Source tree; writes reports/grype.sarif and exits 2 on HIGH or CRITICAL matches
bash scanners/grype/scan.sh dir:./my-project reports

# Reuse an SBOM generated earlier in the release process
bash scanners/grype/scan.sh sbom:./sbom.cdx.json reports

# Scan an image by immutable digest
bash scanners/grype/scan.sh registry:example.com/team/app@sha256:<digest> reports
```

The second argument is an output directory. `GRYPE_FAIL_ON=critical` changes the gate; `GRYPE_FAIL_ON=off` writes a report without a severity gate. Exit code `2` means a finding met the gate; other nonzero codes indicate scan or configuration failure. Keep the SARIF artifact even when a gate fails, and review the package, installed version, fix state, and whether the vulnerable code is reachable before assigning remediation.

[`grype.yaml`](grype.yaml) leaves all findings visible. Add narrowly scoped ignores only after documenting the owner, expiry, and reason in your consuming repository. Refresh the vulnerability database regularly; an old database makes a clean scan weak evidence. Do not commit unredacted reports from private projects.

Reference: [Grype configuration](https://oss.anchore.com/docs/reference/grype/configuration/) and [result filtering](https://oss.anchore.com/docs/guides/vulnerability/filter-results/).
