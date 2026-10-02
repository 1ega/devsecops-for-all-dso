# Azure Key Vault

**Area:** 8. Secure the cloud → Cloud secrets and keys  
**License:** Azure service

[Documentation](https://learn.microsoft.com/azure/key-vault/) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/skills/secrets-management/azure-keyvault)

## What it is for

Secrets, keys, and certificates with Azure RBAC access control.

One vault for secrets, encryption keys, and TLS certificates, with managed identities for applications.

## Install

**Create a vault and a secret**

```bash
az keyvault create --name my-vault --resource-group my-rg --enable-rbac-authorization true
az keyvault secret set --vault-name my-vault --name db-password --value "$DB_PASSWORD"
```

## Output and triage

Turn on soft delete and purge protection for production vaults.

## Concepts to know

- Secret rotation
- Customer-managed keys (KMS)
- Key policies
- Workload identity instead of keys
- Audit logs for secret access

## Related tools

- [AWS Secrets Manager](aws-secrets-manager.md) — Stores secrets with automatic rotation and IAM-based access.
- [Google Secret Manager](gcp-secret-manager.md) — Versioned secrets with IAM and audit logging.
