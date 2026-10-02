# Trivy (image)

**Version covered:** 0.75.0. [Local configs and wrapper](../scanners/trivy/README.md).

**Area:** 3. Harden containers → Container images  
**License:** Apache-2.0  
**Notes:** Container scanning report template included

[GitHub: aquasecurity/trivy](https://github.com/aquasecurity/trivy) · [Documentation](https://trivy.dev/docs/latest/) · [In this repository](https://github.com/1ega/devsecops-for-all-dso/tree/main/scanners/trivy)

## What it is for

Scans built images for OS and library vulnerabilities, secrets, and misconfiguration.

This is what GitLab container scanning runs under the hood. Running it yourself gives you the same report on any tier and full control over thresholds.

> [!WARNING]
> In March 2026 Trivy images on Docker Hub and its GitHub Actions were reported compromised. Pin `aquasec/trivy` by digest.

## Install

**Homebrew**

```bash
brew install trivy
```

## Use

**Scan an image**

```bash
trivy image python:3.12-slim
```

**Fail on critical findings**

```bash
trivy image --exit-code 1 --severity CRITICAL my-app:latest
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
container-scan:
  stage: test
  image:
    name: aquasec/trivy:0.75.0@sha256:af6acf9a6b85dfe389a1941505c0ce9efef52a4719635e1a962f022a3d855daa          # pin by digest
    entrypoint: [""]
  variables:
    FULL_IMAGE_NAME: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    TRIVY_USERNAME: $CI_REGISTRY_USER
    TRIVY_PASSWORD: $CI_REGISTRY_PASSWORD
    TRIVY_AUTH_URL: $CI_REGISTRY
    TRIVY_NO_PROGRESS: "true"
  script:
    - trivy image --exit-code 0 --format template --template "@/contrib/gitlab.tpl"
        --output "$CI_PROJECT_DIR/gl-container-scanning-report.json" "$FULL_IMAGE_NAME"
    - trivy image --exit-code 1 --severity CRITICAL "$FULL_IMAGE_NAME"
  artifacts:
    when: always
    reports:
      container_scanning: gl-container-scanning-report.json
```

## Output and triage

The first command writes the GitLab report; the second fails the job on critical findings. Use `.trivyignore` with a reason for accepted CVEs.

## Concepts to know

- Dockerfile best practices
- Golden and distroless base images
- Non-root users
- Linux capabilities
- Namespaces and cgroups
- Container escape
- Registry hygiene

## Related tools

- [hadolint](hadolint.md) — Dockerfile linter that also checks the shell commands inside RUN.
- [Dockle](dockle.md) — Checks a built image against CIS Docker benchmark and best practices.
- [distroless base images](distroless.md) — Minimal base images with no shell or package manager.
- [skopeo](skopeo.md) — Inspects and copies images between registries and archives without a Docker daemon.
- [crane](crane.md) — Small CLI for registry operations: digests, tags, manifests, and filesystem export.

## Tuning and acceptance

Use immutable image references and a current database/check bundle. Keep unfixed
findings visible; accept risk only with asset scope, owner and expiry. Confirm
ecosystem/config-parser coverage and skipped files. Test a known positive and
negative fixture using [the local tests](../scanners/trivy/tests/README.md), retain
private reports, and distinguish tool failures from finding exit codes.
