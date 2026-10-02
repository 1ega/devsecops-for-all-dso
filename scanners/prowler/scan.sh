#!/usr/bin/env bash
set -euo pipefail

if (( $# < 2 )); then
  echo 'Usage: scan.sh <aws|azure|gcp|kubernetes> <output-directory> [prowler-options...]' >&2
  exit 64
fi
if ! command -v prowler >/dev/null 2>&1; then
  echo 'Prowler is required: https://github.com/prowler-cloud/prowler' >&2
  exit 69
fi
provider=$1
output_dir=$2
shift 2
case "$provider" in
  aws|azure|gcp|kubernetes) ;;
  *) echo 'Provider must be aws, azure, gcp, or kubernetes' >&2; exit 64 ;;
esac
umask 077
mkdir -p -- "$output_dir"
prowler "$provider" -M json-ocsf html -o "$output_dir" "$@"
