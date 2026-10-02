# secureCodeBox

**Area:** 9. Run the program → Vulnerability management and release gates  
**License:** Apache-2.0

[GitHub: secureCodeBox/secureCodeBox](https://github.com/secureCodeBox/secureCodeBox) · [Documentation](https://www.securecodebox.io/docs/getting-started/installation)

## What it is for

Runs scanners as Kubernetes jobs on a schedule and ships results to DefectDojo.

For continuous scanning of many targets: nmap, ZAP, nuclei, Trivy, and others run inside the cluster and report automatically.

## Install

**Operator and a scanner (Helm)**

```bash
helm --namespace securecodebox-system upgrade --install --create-namespace \
  securecodebox-operator oci://ghcr.io/securecodebox/helm/operator
helm install nmap oci://ghcr.io/securecodebox/helm/nmap
```

## Use

**Start a scan**

```bash
kubectl apply -f nmap-scan.yaml
kubectl get scans
```

## Output and triage

Install the `persistence-defectdojo` hook to send every result to DefectDojo.

## Concepts to know

- Vulnerability lifecycle
- CVSS and SSVC
- KEV catalog
- Prioritization
- Deployment and quality gates
- Risk acceptance with expiry
- Remediation SLAs
- Vulnerability disclosure program

## Related tools

- [DefectDojo](defectdojo.md) — Imports results from 200+ scanners, deduplicates them, and tracks them per product.
- [Dependency-Track](dependency-track.md) — Continuously re-checks uploaded SBOMs against new vulnerability data.
