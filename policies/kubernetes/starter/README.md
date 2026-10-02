# Small Kubernetes baseline

Original templates with Restricted Pod Security, a hardened workload, default
network denial and explicit cluster-DNS allowance. Inspect all placeholders and
cluster-specific behavior before applying to a staging namespace.

1. Set the namespace and Pod Security minor version to your tested cluster.
   Start existing namespaces with warn/audit; enforce after compatibility review.
2. Replace the workload's deliberately invalid image with a tested application
   digest, choose UID/ports/probes/resources and disable service-account token
   automount unless API access is required.
3. Confirm the CNI enforces NetworkPolicy. Review CoreDNS labels and NodeLocal
   DNS paths; the provided DNS policy assumes namespace/pod selectors matching
   standard CoreDNS. Add required app/ingress/database/monitoring allowances.
4. Apply policies in staging and test allowed requests plus blocked cross-pod
   and external paths. Default-deny affects existing selected workloads too.
5. Test a privileged pod is rejected and the permitted hardened workload starts.
   Review RBAC, namespace administration and token permissions separately.

```bash
kubectl apply --dry-run=server -f policies/kubernetes/starter/namespace.yaml
trivy config --config scanners/trivy/config.yaml policies/kubernetes/starter/
```

The workload cannot pull until its image placeholder is replaced. Do not apply
these app policies to the Falco sensor namespace. See [Pod Security](https://kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/)
and [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/).
