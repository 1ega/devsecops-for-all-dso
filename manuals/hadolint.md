# hadolint

**Version reviewed:** v2.15.1 ([official release](https://github.com/hadolint/hadolint/releases/tag/v2.15.1)); metadata checked 2026-10-02.

**Area:** 3. Harden containers → Container images  
**License:** GPL-3.0  
**Notes:** Code quality report format  
**Recommended first choice in this topic.**

[GitHub: hadolint/hadolint](https://github.com/hadolint/hadolint) · [Documentation](https://github.com/hadolint/hadolint#readme)

## What it is for

Dockerfile linter that also checks the shell commands inside RUN.

Catches unpinned base images, root users, and fragile shell in seconds, before anything is built. The easiest container check to add first.

> [!WARNING]
> The default image has no shell. In GitLab use the `latest-debian` or `latest-alpine` tag. GitLab deprecated the codeclimate report format in 17.3; prefer SARIF if you collect results elsewhere.

## Install

**Homebrew or container**

```bash
brew install hadolint
# or
docker run --rm -i hadolint/hadolint < Dockerfile
```

## Use

**Lint a Dockerfile**

```bash
hadolint Dockerfile
```

**SARIF output**

```bash
hadolint -f sarif Dockerfile > hadolint.sarif
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
hadolint:
  stage: test
  image: hadolint/hadolint:v2.15.1-debian@sha256:9a3944b7fddcb947d1ffd90829ac1a6e5c30479223358f249d8b96c7d0019e27
  script:
    - mkdir -p reports
    - hadolint -f gitlab_codeclimate Dockerfile > reports/hadolint.json
  artifacts:
    when: always
    reports:
      codequality: reports/hadolint.json
```

## Output and triage

Fails at or above `--failure-threshold` (default info). Ignore a reviewed rule inline with `# hadolint ignore=DL3008`.

## Concepts to know

- Dockerfile best practices
- Golden and distroless base images
- Non-root users
- Linux capabilities
- Namespaces and cgroups
- Container escape
- Registry hygiene

## Related tools

- [Trivy (image)](trivy-image.md) — Scans built images for OS and library vulnerabilities, secrets, and misconfiguration.
- [Dockle](dockle.md) — Checks a built image against CIS Docker benchmark and best practices.
- [distroless base images](distroless.md) — Minimal base images with no shell or package manager.
- [skopeo](skopeo.md) — Inspects and copies images between registries and archives without a Docker daemon.
- [crane](crane.md) — Small CLI for registry operations: digests, tags, manifests, and filesystem export.
