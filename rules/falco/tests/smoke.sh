#!/usr/bin/env bash
# Linux Docker host only. Creates a privileged sensor and disposable workloads.
set -euo pipefail
test_dir="$(cd "$(dirname "$0")" && pwd)"
falco_dir="$(cd "$test_dir/.." && pwd)"
falco_image='falcosecurity/falco:0.45.0@sha256:788f1129c542171813083d4afc61b16730a47dde8c23d9c39370acef996349b6'
test_image='python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d'
if [[ "$(uname -s)" != Linux ]]; then
  echo 'Run this on a disposable Linux Docker host.' >&2; exit 2
fi
report_dir="${DSO_REPORT_DIR:-$(mktemp -d)}"
mkdir -p "$report_dir"
sensor_id=''; positive_id=''; negative_id=''
cleanup() {
  if [[ -n "$sensor_id" ]]; then
    docker logs "$sensor_id" >"$report_dir/falco.jsonl" 2>&1 || true
  fi
  for identity in "$positive_id" "$negative_id" "$sensor_id"; do
    if [[ -n "$identity" ]]; then docker rm -f "$identity" >/dev/null || true; fi
  done
}
trap cleanup EXIT
docker pull "$test_image" >/dev/null
sensor_id="$(docker run -d --privileged --pid=host -p 127.0.0.1::8765 --entrypoint /usr/bin/falco \
  -v /proc:/host/proc:ro -v /sys:/host/sys:ro \
  -v "$falco_dir:/dso:ro" "$falco_image" \
  -r /dso/dso-runtime.yaml -o engine.kind=modern_ebpf \
  -o rule_matching=all -o json_output=true -o priority=notice -o stdout_output.enabled=true \
  -o syslog_output.enabled=false -o buffered_outputs=false)"
health_address="$(docker port "$sensor_id" 8765/tcp)"
health_url="http://$health_address/healthz"
ready=false
for attempt in {1..30}; do
  if python3 -c 'import sys, urllib.request; urllib.request.urlopen(sys.argv[1], timeout=1)' "$health_url" >/dev/null 2>&1; then
    ready=true; break
  fi
  if [[ "$(docker inspect -f '{{.State.Running}}' "$sensor_id")" != true ]]; then
    docker logs "$sensor_id" >&2; exit 2
  fi
  sleep 1
done
if [[ "$ready" != true ]]; then echo 'Falco health check did not become ready' >&2; exit 2; fi
# /healthz answers before the syscall probe is attached; wait for a real alert.
captured=false
for attempt in {1..30}; do
  docker run --rm --network none --cap-drop ALL --security-opt no-new-privileges "$test_image" \
    sh -c 'cp /usr/bin/true /tmp/dso-canary && /tmp/dso-canary' >/dev/null 2>&1 || true
  if docker logs "$sensor_id" 2>&1 | grep -qF '"rule":"DSO Executable launched from temporary directory"'; then
    captured=true; break
  fi
  sleep 1
done
if [[ "$captured" != true ]]; then echo 'Falco did not report the canary event' >&2; exit 2; fi
for mode in positive negative; do
  # Unconfined seccomp is restricted to the fixture container for PTRACE_TRACEME.
  identity="$(docker create --network none --cap-drop ALL \
    --security-opt no-new-privileges --security-opt seccomp=unconfined \
    -v "$test_dir/generate.py:/generate.py:ro" "$test_image" python /generate.py "$mode")"
  if [[ "$mode" == positive ]]; then positive_id="$identity"; else negative_id="$identity"; fi
  docker start -a "$identity"
  [[ "$(docker inspect -f '{{.State.ExitCode}}' "$identity")" == 0 ]] || exit 2
done
sleep 3
docker logs "$sensor_id" >"$report_dir/falco.jsonl" 2>&1
python3 "$test_dir/assert_alerts.py" "$report_dir/falco.jsonl" "$positive_id" "$negative_id"
echo "Test logs: $report_dir/falco.jsonl"
