# Dockle

**Version reviewed:** v0.4.15 ([official release](https://github.com/goodwithtech/dockle/releases/tag/v0.4.15)); metadata checked 2026-10-02.

**Area:** 3. Harden containers → Container images  
**License:** Apache-2.0

[GitHub: goodwithtech/dockle](https://github.com/goodwithtech/dockle) · [Documentation](https://github.com/goodwithtech/dockle#readme)

## What it is for

Checks a built image against CIS Docker benchmark and best practices.

Complements vulnerability scanning: finds root users, setuid files, secrets in environment variables, and missing health checks.

## Install

**Homebrew**

```bash
brew install goodwithtech/r/dockle
```

## Use

**Check an image, fail on warnings**

```bash
dockle --exit-code 1 --exit-level warn my-app:latest
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
dockle:
  stage: test
  image:
    name: goodwithtech/dockle:v0.4.15@sha256:eade932f793742de0aa8755406c7677cd7696f8675b6180926f7eeffa7abe6b9
    entrypoint: [""]
  variables:
    DOCKLE_USERNAME: $CI_REGISTRY_USER
    DOCKLE_PASSWORD: $CI_REGISTRY_PASSWORD
  script:
    - dockle -f sarif -o dockle.sarif --exit-code 1 "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
  artifacts:
    when: always
    paths: [dockle.sarif]
```

## Output and triage

Exits 0 by default even with findings; `--exit-code 1` fails on WARN and FATAL. Skip a reviewed check with `-i CIS-DI-0001`.

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
- [Trivy (image)](trivy-image.md) — Scans built images for OS and library vulnerabilities, secrets, and misconfiguration.
- [distroless base images](distroless.md) — Minimal base images with no shell or package manager.
- [skopeo](skopeo.md) — Inspects and copies images between registries and archives without a Docker daemon.
- [crane](crane.md) — Small CLI for registry operations: digests, tags, manifests, and filesystem export.
