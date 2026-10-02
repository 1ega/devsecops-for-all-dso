#!/usr/bin/env bash
# Native Trivy 0.75.0; preserve reports and separate findings from tool errors.
set -euo pipefail
if (( $# != 3 )); then
  echo 'Usage: scan.sh <image|config> <target> <private-report-directory>' >&2; exit 64
fi
mode=$1; target=$2; report_dir=$3
case "$mode" in image|config) ;; *) echo 'Mode must be image or config' >&2; exit 64 ;; esac
if [[ "$target" == -* ]]; then echo 'Target must not be an option' >&2; exit 64; fi
if ! command -v trivy >/dev/null; then echo 'Install reviewed Trivy 0.75.0' >&2; exit 69; fi
version="$(trivy --version | head -n 1)"
if [[ "$version" != 'Version: 0.75.0' ]]; then echo "Expected Trivy 0.75.0; got $version" >&2; exit 69; fi
if [[ "$mode" == image && ! "$target" =~ @sha256:[a-f0-9]{64}$ ]]; then
  echo 'Image target must include its immutable sha256 digest' >&2; exit 64
fi
umask 077
mkdir -p "$report_dir"
script_dir="$(cd "$(dirname "$0")" && pwd)"
extension=json
if [[ "$mode" == config ]]; then extension=sarif; fi
temporary_report="$(mktemp "$report_dir/.trivy.XXXXXXXX")"
trap 'rm -f "$temporary_report"' EXIT
set +e
trivy "$mode" --config "$script_dir/$mode.yaml" --exit-code 10 \
  --output "$temporary_report" "$target"
scan_rc=$?
set -e
case "$scan_rc" in
  0|10)
    if [[ ! -s "$temporary_report" ]]; then echo 'Scanner produced no report' >&2; exit 2; fi
    mv "$temporary_report" "$report_dir/trivy-$mode.$extension"
    if [[ "$scan_rc" == 10 ]]; then exit 1; fi ;;
  *) echo "Trivy execution failed with exit $scan_rc" >&2; exit 2 ;;
esac
