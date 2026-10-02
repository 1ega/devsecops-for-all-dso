# distroless base images

**Area:** 3. Harden containers → Container images  
**License:** Apache-2.0

[GitHub: GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless) · [Documentation](https://github.com/GoogleContainerTools/distroless#readme) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/policies/containers/distroless-examples)

## What it is for

Minimal base images with no shell or package manager.

Removing the shell and package manager removes most of what an attacker would use after a break-in, and most of the CVEs scanners report.

## Install

**Use as the final stage of a multi-stage build**

```dockerfile
FROM golang:1.23 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /app .

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /app /app
USER nonroot
ENTRYPOINT ["/app"]
```

## Output and triage

Debug with the `:debug` tags, which add a busybox shell; never ship them to production. Reference Dockerfiles for other languages are in this repository.

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
- [skopeo](skopeo.md) — Inspects and copies images between registries and archives without a Docker daemon.
- [crane](crane.md) — Small CLI for registry operations: digests, tags, manifests, and filesystem export.
