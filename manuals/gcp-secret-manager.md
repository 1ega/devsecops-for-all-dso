# Google Secret Manager

**Area:** 8. Secure the cloud → Cloud secrets and keys  
**License:** Google Cloud service

[Documentation](https://cloud.google.com/secret-manager/docs) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/skills/secrets-management/gcp-secret-manager)

## What it is for

Versioned secrets with IAM and audit logging.

Integrates with workload identity on GKE and Cloud Run, so services read secrets without key files.

## Install

**Create a secret and add a version**

```bash
gcloud secrets create db-password --replication-policy=automatic
printf '%s' "$DB_PASSWORD" | gcloud secrets versions add db-password --data-file=-
```

## Use

**Read the latest version**

```bash
gcloud secrets versions access latest --secret=db-password
```

## Concepts to know

- Secret rotation
- Customer-managed keys (KMS)
- Key policies
- Workload identity instead of keys
- Audit logs for secret access

## Related tools

- [AWS Secrets Manager](aws-secrets-manager.md) — Stores secrets with automatic rotation and IAM-based access.
- [Azure Key Vault](azure-key-vault.md) — Secrets, keys, and certificates with Azure RBAC access control.
