# skopeo

**Area:** 3. Harden containers → Container images  
**License:** Apache-2.0

[GitHub: podman-container-tools/skopeo](https://github.com/podman-container-tools/skopeo) · [Documentation](https://github.com/podman-container-tools/skopeo#readme)

## What it is for

Inspects and copies images between registries and archives without a Docker daemon.

Lets scanners pull an image as a file in CI without Docker-in-Docker or privileged runners, then scan the archive.

## Install

**Homebrew**

```bash
brew install skopeo
```

## Use

**Inspect an image and read its digest**

```bash
skopeo inspect docker://nginx:1.25 | jq '.Digest'
```

**Save an image as an OCI archive for scanning**

```bash
skopeo copy docker://nginx:1.25 oci-archive:nginx.tar
```

## Output and triage

Uses credentials from `skopeo login`, `docker login`, or `--creds`.

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
- [Dockle](dockle.md) — Checks a built image against CIS Docker benchmark and best practices.
- [distroless base images](distroless.md) — Minimal base images with no shell or package manager.
- [crane](crane.md) — Small CLI for registry operations: digests, tags, manifests, and filesystem export.
