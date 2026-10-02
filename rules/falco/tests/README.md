# Falco validation

Run from the repository root:

```bash
python3 tools/validation/check_repo.py
bash rules/falco/validate.sh
# Disposable Linux Docker host only:
bash rules/falco/tests/smoke.sh
```

The repository checker validates YAML, metadata and the positive/negative
scenario contract. `validate.sh` compiles actual filters with Falco 0.45.0 and
the example override. The smoke test starts a privileged sensor, then two
isolated containers without network access or host data mounts. Because
`/healthz` answers before the syscall probe is attached, it first waits until a
canary container's temporary-directory executable produces an alert. Its positive
container generates all 16 named behaviors using dummy files, harmless renamed
`true` and `sh` binaries, its own Unix socket, a pseudoterminal, a memfd and
self-tracing. The negative container opens an ordinary file and executes `true`.

`assert_alerts.py` requires every local rule to alert for the positive container
and none for the negative container; zero alerts fails. Test containers are
removed on exit. Logs remain in the printed temporary directory; set
`DSO_REPORT_DIR` to choose a private destination. No deployment to a real cluster
is performed. Keep test logs out of public git.

These checks do not establish real-world recall or false-positive rates.
`scenarios.json` records the rule-specific non-match cases to exercise while
tuning. In particular, test failed syscalls, approved process exceptions and
alternate credential/token mount paths in your staging environment.

**Validation status (2026-10-02):** `validate.sh` compiles both files with Falco
0.45.0, and a broken condition makes it exit 1. The smoke test passed 16/16 positive
rules with no negative alerts using `modern_ebpf` on a Docker Desktop Linux VM
(LinuxKit 6.12, arm64), with only the `uname` guard bypassed. CI runs compilation
on every push; the smoke test runs through the manual workflow dispatch. The
rule-specific non-match cases in `scenarios.json` are not automated yet.
