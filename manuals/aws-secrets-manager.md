# AWS Secrets Manager

**Area:** 8. Secure the cloud → Cloud secrets and keys  
**License:** AWS service (paid)  
**Recommended first choice in this topic.**

[Documentation](https://docs.aws.amazon.com/secretsmanager/) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/skills/secrets-management/aws-secrets-manager)

## What it is for

Stores secrets with automatic rotation and IAM-based access.

Rotation is built in for RDS and other databases, and every read is logged in CloudTrail.

## Install

**Create and read a secret**

```bash
aws secretsmanager create-secret --name prod/db/password --secret-string "$DB_PASSWORD"
aws secretsmanager get-secret-value --secret-id prod/db/password
```

## Output and triage

Grant `secretsmanager:GetSecretValue` per secret ARN, never on `*`.

## Concepts to know

- Secret rotation
- Customer-managed keys (KMS)
- Key policies
- Workload identity instead of keys
- Audit logs for secret access

## Related tools

- [Azure Key Vault](azure-key-vault.md) — Secrets, keys, and certificates with Azure RBAC access control.
- [Google Secret Manager](gcp-secret-manager.md) — Versioned secrets with IAM and audit logging.
