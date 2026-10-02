# Falco

**Area:** 6. Guard Kubernetes → Runtime detection  
**License:** Apache-2.0  
**Recommended first choice in this topic.**

[GitHub: falcosecurity/falco](https://github.com/falcosecurity/falco) · [Documentation](https://falco.org/docs/)

## What it is for

eBPF-based runtime detection for containers, Kubernetes, and hosts.

The CNCF standard for runtime threat detection. Default rules already catch shells in containers, reads of sensitive files, and privilege escalation.

## Install

**Helm**

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco -n falco --create-namespace
```

## Use

**Watch alerts**

```bash
kubectl logs -n falco -l app.kubernetes.io/name=falco -f
```

## Output and triage

Send alerts to your SIEM or chat with Falcosidekick, and tune noisy rules with exceptions rather than disabling them.

## Concepts to know

- Container escape
- Process monitoring
- Egress control
- eBPF
- Alert routing
