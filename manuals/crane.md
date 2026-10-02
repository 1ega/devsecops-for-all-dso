# crane

**Version reviewed:** v0.22.1 ([official release](https://github.com/google/go-containerregistry/releases/tag/v0.22.1)); metadata checked 2026-10-02.

**Area:** 3. Harden containers → Container images  
**License:** Apache-2.0

[GitHub: google/go-containerregistry](https://github.com/google/go-containerregistry) · [Documentation](https://github.com/google/go-containerregistry/tree/main/cmd/crane)

## What it is for

Small CLI for registry operations: digests, tags, manifests, and filesystem export.

Resolve tags to digests for pinning, list tags, and export an image filesystem for malware or secret scans.

## Install

**Homebrew or Go**

```bash
brew install crane
# or
go install github.com/google/go-containerregistry/cmd/crane@v0.22.1
```

## Use

**Resolve a tag to a digest**

```bash
crane digest nginx:1.25
```

**Export the image filesystem**

```bash
mkdir rootfs && crane export nginx:1.25 - | tar -x -C rootfs
```

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
- [skopeo](skopeo.md) — Inspects and copies images between registries and archives without a Docker daemon.
