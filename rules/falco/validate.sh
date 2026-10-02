#!/usr/bin/env bash
# Compile conditions with the real Falco engine, without loading kernel drivers.
set -euo pipefail
repo_dir="$(cd "$(dirname "$0")/../.." && pwd)"
image='falcosecurity/falco:0.45.0@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6'
docker run --rm --entrypoint /usr/bin/falco \
  -v "$repo_dir/rules/falco:/dso:ro" "$image" \
  -o engine.kind=nodriver -o load_plugins=[] \
  -V /dso/dso-runtime.yaml -V /dso/exceptions.example.yaml
