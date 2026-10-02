# HashiCorp Vault

**Area:** 2. Secure the pipeline → Secrets management  
**License:** BUSL-1.1  
**Notes:** Native secrets: integration (Premium)  
**Recommended first choice in this topic.**

[GitHub: hashicorp/vault](https://github.com/hashicorp/vault) · [Documentation](https://developer.hashicorp.com/vault/docs)

## What it is for

Central secret store with dynamic credentials and JWT login for GitLab jobs.

GitLab jobs log in with their OIDC token, so no secret is stored in GitLab at all. Vault can also mint short-lived database and cloud credentials per job.

> [!WARNING]
> Vault is under the Business Source License. OpenBao (openbao/openbao) is an MPL-2.0 fork with a compatible API if you need an open-source license.

## Install

**Homebrew**

```bash
brew tap hashicorp/tap
brew install hashicorp/tap/vault
```

**Development server (never use in production)**

```bash
vault server -dev
```

## Use

**Trust GitLab job tokens (JWT auth)**

```bash
vault auth enable jwt
vault write auth/jwt/config \
  oidc_discovery_url="https://gitlab.com" \
  bound_issuer="https://gitlab.com"
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
deploy:
  stage: deploy
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  secrets:
    DATABASE_PASSWORD:
      vault: production/db/password@ops   # path/field@mount
      token: $VAULT_ID_TOKEN
  variables:
    VAULT_SERVER_URL: https://vault.example.com
  script:
    - ./deploy.sh                          # DATABASE_PASSWORD is a file path
```

## Output and triage

Bind Vault roles to claims such as `project_path` and `ref_protected` so only protected branches of a given project can read production secrets.

## Concepts to know

- Secret zero
- Short-lived credentials
- Workload identity
- Cloud secrets managers and KMS
- Encryption at rest in git
- Rotation

## Related tools

- [SOPS](sops.md) — Encrypts values inside YAML, JSON, and env files so they can live in git.
- [External Secrets Operator](external-secrets.md) — Syncs secrets from Vault or cloud secret managers into Kubernetes Secrets.
