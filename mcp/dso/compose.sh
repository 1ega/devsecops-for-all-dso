#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
case "${DSO_ROOT:-}" in
  /*) ;;
  *) printf 'DSO: set DSO_ROOT to an absolute existing directory\n' >&2; exit 2 ;;
esac
[[ -d "$DSO_ROOT" ]] || { printf 'DSO: DSO_ROOT is not a directory\n' >&2; exit 2; }
exec docker compose -f "$script_dir/compose.yaml" "$@"
