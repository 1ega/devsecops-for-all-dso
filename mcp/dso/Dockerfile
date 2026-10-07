# Reviewed Gitleaks v8.30.1 source, rebuilt with a patched Go toolchain and x/crypto/x/text:
# the upstream binary carries fixed Go CVEs. Module downloads are verified by go.sum/sumdb.
FROM golang:1.26.6-alpine@sha256:3889b425f035be855a72fb4755265311293b6d414521f0a519d819df32222d83 AS gitleaks
ARG GITLEAKS_COMMIT=83d9cd684c87d95d656c1458ef04895a7f1cbd8e
RUN apk add --no-cache git \
    && git clone --quiet --depth 1 --branch v8.30.1 https://github.com/gitleaks/gitleaks /src \
    && test "$(git -C /src rev-parse HEAD)" = "$GITLEAKS_COMMIT"
WORKDIR /src
RUN go get golang.org/x/crypto@v0.55.0 golang.org/x/text@v0.41.0 \
    && go mod tidy \
    && CGO_ENABLED=0 go build -trimpath \
       -ldflags "-s -w -X=github.com/zricethezav/gitleaks/v8/version.Version=v8.30.1" \
       -o /usr/bin/gitleaks .
FROM aquasec/trivy:0.75.0@sha256:af6acf9a6b85dfe389a1941505c0ce9efef52a4719635e1a962f022a3d855daa AS trivy
FROM python:3.12-slim@sha256:dddfd7e07f9d15aeeca61529320492139d21cac7f0070c00609243e51e4e0016

LABEL org.opencontainers.image.title="DSO CLI and MCP" \
      org.opencontainers.image.source="https://github.com/1ega/devsecops-for-all-dso"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DSO_CACHE_DIR=/cache
COPY mcp/dso/debian.sources /etc/apt/sources.list.d/debian.sources
# Signed, timestamp-pinned Debian indices determine the complete upgrade set.
# git is unnecessary: DSO scans a private snapshot with explicit file selection.
RUN apt-get update && apt-get -y dist-upgrade \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home dso \
    && mkdir -m 1777 /cache \
    && find / -xdev -type f -perm /6000 -exec chmod a-s '{}' +
WORKDIR /opt/dso
COPY mcp/dso/requirements-standalone.lock mcp/dso/
RUN python -m pip install --no-cache-dir --require-hashes -r mcp/dso/requirements-standalone.lock \
    && python -m pip uninstall -y pip
COPY --from=gitleaks /usr/bin/gitleaks /usr/local/bin/gitleaks
COPY --from=trivy /usr/local/bin/trivy /usr/local/bin/trivy
COPY tools/dso/dso.py tools/dso/scanning.py tools/dso/runtime.py tools/dso/reports.py tools/dso/manifest.py \
     tools/dso/inventory.py tools/dso/register.py tools/dso/config.py tools/dso/console.py tools/dso/sources.py \
     tools/dso/plugins.json tools/dso/publish_report.py tools/dso/
COPY tools/dso/plugins/ tools/dso/plugins/
COPY baseline/controls.json baseline/controls.json
# The manifest validates every profile at startup, including rules for optional scanners.
# Keep the full packs and their license/attribution files in the standalone package.
COPY rules/semgrep/ rules/semgrep/
COPY rules/secrets/ rules/secrets/
COPY rules/yara/ rules/yara/
COPY mcp/dso/server.py mcp/dso/
COPY LICENSE THIRD_PARTY_NOTICES.md ./
COPY mcp/dso/licenses/ licenses/
# Fail the build if the packaged CLI cannot load its manifest or bundled rule paths.
RUN python tools/dso/dso.py --version
# SBOM generation performs inventory only, without a vulnerability database.
RUN trivy rootfs --offline-scan --format cyclonedx \
    --skip-dirs /proc --skip-dirs /sys --skip-dirs /dev \
    --output /opt/dso/sbom.cdx.json /
USER 10001:10001
VOLUME ["/cache"]
ENTRYPOINT ["python", "/opt/dso/mcp/dso/server.py"]
CMD ["--root", "/workspace", "--engine", "native"]
