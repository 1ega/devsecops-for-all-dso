# External Secrets Operator

**Area:** 2. Secure the pipeline → Secrets management  
**License:** Apache-2.0

[GitHub: external-secrets/external-secrets](https://github.com/external-secrets/external-secrets) · [Documentation](https://external-secrets.io/)

## What it is for

Syncs secrets from Vault or cloud secret managers into Kubernetes Secrets.

Applications keep reading normal Kubernetes Secrets while the source of truth stays in Vault, AWS, GCP, or Azure.

## Install

**Helm**

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace
```

## Use

**Check that the operator is running**

```bash
kubectl get pods -n external-secrets
kubectl get secretstores,externalsecrets -A
```

## Output and triage

Define a SecretStore per namespace and an ExternalSecret per application secret. Limit who can create SecretStores: they decide which vault paths a namespace can read.

## Concepts to know

- Secret zero
- Short-lived credentials
- Workload identity
- Cloud secrets managers and KMS
- Encryption at rest in git
- Rotation

## Related tools

- [HashiCorp Vault](vault.md) — Central secret store with dynamic credentials and JWT login for GitLab jobs.
- [SOPS](sops.md) — Encrypts values inside YAML, JSON, and env files so they can live in git.
