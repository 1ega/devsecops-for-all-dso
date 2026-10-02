#!/usr/bin/env bash
set -euo pipefail

if (( $# < 1 || $# > 2 )); then
  echo 'Usage: scan.sh <grype-source> [output-directory]' >&2
  exit 64
fi
if ! command -v grype >/dev/null 2>&1; then
  echo 'Grype is required: https://github.com/anchore/grype' >&2
  exit 69
fi

source_arg=$1
if [[ "$source_arg" == -* ]]; then
  echo "Source must be a Grype target, not an option" >&2; exit 64
fi
umask 077
report_dir=${2:-reports}
fail_on=${GRYPE_FAIL_ON:-high}
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
mkdir -p -- "$report_dir"

args=(-c "$script_dir/grype.yaml" "$source_arg" -o sarif --file "$report_dir/grype.sarif")
if [[ "$fail_on" != off ]]; then
  case "$fail_on" in
    negligible|low|medium|high|critical) args+=(--fail-on "$fail_on") ;;
    *) echo 'GRYPE_FAIL_ON must be off, negligible, low, medium, high, or critical' >&2; exit 64 ;;
  esac
fi
grype "${args[@]}"
