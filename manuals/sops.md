# SOPS

**Area:** 2. Secure the pipeline → Secrets management  
**License:** MPL-2.0

[GitHub: getsops/sops](https://github.com/getsops/sops) · [Documentation](https://getsops.io/docs/)

## What it is for

Encrypts values inside YAML, JSON, and env files so they can live in git.

Good for GitOps and small teams: secrets stay next to the code, encrypted with age, PGP, or a cloud KMS, and diffs remain readable.

## Install

**Homebrew**

```bash
brew install sops age
```

## Use

**Create a key and encrypt a file**

```bash
age-keygen -o key.txt
sops encrypt --age <public-key> secrets.yaml > secrets.enc.yaml
```

**Decrypt**

```bash
SOPS_AGE_KEY_FILE=key.txt sops decrypt secrets.enc.yaml
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
decrypt:
  stage: deploy
  image: alpine:3.20
  before_script:
    - apk add --no-cache sops
  script:
    # SOPS_AGE_KEY is a protected, masked CI/CD variable
    - sops decrypt secrets.enc.yaml > secrets.yaml
    - ./deploy.sh
```

## Output and triage

Store the private key only in a protected variable or a KMS. Add a `.sops.yaml` creation rule so everyone encrypts with the same keys.

## Concepts to know

- Secret zero
- Short-lived credentials
- Workload identity
- Cloud secrets managers and KMS
- Encryption at rest in git
- Rotation

## Related tools

- [HashiCorp Vault](vault.md) — Central secret store with dynamic credentials and JWT login for GitLab jobs.
- [External Secrets Operator](external-secrets.md) — Syncs secrets from Vault or cloud secret managers into Kubernetes Secrets.
