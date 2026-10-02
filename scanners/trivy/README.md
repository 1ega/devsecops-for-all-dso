# Trivy configurations

[image.yaml](image.yaml) scans image vulnerabilities and secrets, blocking HIGH
and CRITICAL including unfixed vulnerabilities. [config.yaml](config.yaml)
blocks HIGH/CRITICAL IaC misconfiguration and outputs SARIF. Trivy 0.75.0:

```bash
trivy image --config scanners/trivy/image.yaml --output /private/path/image.json IMAGE@sha256:DIGEST
trivy config --config scanners/trivy/config.yaml --output /private/path/iac.sarif /path/to/iac
```

Install the reviewed upstream 0.75.0 release and verify its checksum. Use a
resolved production image digest; a tag can point to another build. Network is
needed for vulnerability data/check bundles unless approved mirrors are used.
Reports may contain secrets; restrict access. These are invocation configs, not
proof of cluster/deployed-state compliance. See [image manual](../../manuals/trivy-image.md)
and [config manual](../../manuals/trivy-config.md).

Use [scan.sh](scan.sh) for a common invocation: `bash scanners/trivy/scan.sh config /path/to/iac /private/reports` or `image IMAGE@sha256:DIGEST /private/reports`. It requires 0.75.0 and returns 0 clean, 1 gated findings, 2 scanner/missing-report failure, 64 invalid arguments or 69 unavailable/wrong version. Reports replace only completed scans; never ingest a previous report after a failed run.
