# Containers

Dockerfile and image controls: non-root users, minimal base images, base images pinned by digest, no secrets in layers, and no known critical vulnerabilities. A set of hardened reference Dockerfiles can live here as allowed examples.

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| hadolint | [hadolint/hadolint](https://github.com/hadolint/hadolint) | Dockerfile linter |
| Trivy | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Image vulnerabilities and misconfiguration |
| Grype | [anchore/grype](https://github.com/anchore/grype) | Alternative image scanner |
| Dockle | [goodwithtech/dockle](https://github.com/goodwithtech/dockle) | CIS checks for images |

Related skill: [container-hardening](../../skills/kubernetes-containers/container-hardening/SKILL.md).

**Status:** Structure only; no policies are published yet.
