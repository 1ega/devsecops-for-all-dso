# GitLab CI starter scans

Copy this into the application, setting the repository path and reviewed commit:

```yaml
include:
  - project: group/devsecopsforall
    ref: FULL_COMMIT_SHA
    file: /integrations/gitlab-ci/security.yml
stages: [test]
```

`include:project` needs a mirror of this repository on your GitLab instance.
Without one, include the file from GitHub at a reviewed commit:

```yaml
include:
  - remote: https://raw.githubusercontent.com/1ega/devsecopsforall/FULL_COMMIT_SHA/integrations/gitlab-ci/security.yml
stages: [test]
```

The job uses stage `test`; merge it into existing stages. A dedicated runner
with a working Docker daemon, POSIX shell and registry/database network access
is required. Docker access can control the runner host: use disposable isolated
runners for untrusted merge requests, without production credentials or shared
privileged build state. Do not expose a remote Docker daemon to PR jobs.

[Template](security.yml): pinned images, read-only source, private SARIF artifacts
for seven days; Semgrep uses the registry `p/default` ruleset. Secret findings block; dependency/SAST findings are report-only;
execution errors or missing reports fail. Set `DSO_SECRETS`, `DSO_SCA`, `DSO_SAST`
to `false` only for a documented inapplicable check. Test expected findings and
scanner failures before requiring the job. See [CI hardening](../../guides/cicd-hardening.md).

Optional [infrastructure.yml](infrastructure.yml) adds a Trivy IaC job and an image job when `DSO_IMAGE_DIGEST` is set to a full immutable reference. It uses container jobs, blocks HIGH/CRITICAL and errors, and requires an appropriately isolated runner. Supply private-registry access only in protected trusted jobs.

## Normalized finding gate

Use [dso-gate.yml](dso-gate.yml) for the shared CLI/report/delta gate. The runner
needs Bash 3.2+, Python 3.10+, git, and a Docker CLI and daemon. With a
socket-mounted or remote daemon, the client's `TMPDIR` must exist at the same
absolute path for the daemon; otherwise the scan stops with `mount_visibility`
instead of scanning an empty directory. Include the file at a reviewed immutable
revision and set `DSO_KIT_REF` to the same 40-character commit.

| Variable | Default | Meaning |
| --- | --- | --- |
| `DSO_KIT_REF` | required | Reviewed kit commit; must be reachable from `DSO_KIT_BRANCH` |
| `DSO_KIT_URL` | GitHub kit repository | HTTPS URL of the kit repository or an internal mirror |
| `DSO_KIT_BRANCH` | `main` | Protected kit branch |
| `DSO_BASELINE_REF` | empty | Optional reviewed caller commit that holds the baseline |
| `DSO_BASELINE_BRANCH` | `main` | Protected caller branch that must contain that commit |
| `DSO_BASELINE_PATH` | `.security/dso-baseline.json` | Baseline path in that commit |
| `DSO_FAIL_ON` | `high` | `info`, `low`, `medium`, `high` or `critical` |

The baseline is read from the selected commit with `git show`, not from the merge
request worktree; use `CI_PROJECT_PATH` as its project ID. Shallow clones need
enough history for the ancestry check; raise `GIT_DEPTH` if it fails. Without a
baseline, findings at or above the threshold and unknown severity block.
Incomplete scans fail. The normalized report is published to `reports/dso.json`
(mode 0600, never through a symlink) and retained for seven days, even when the
gate fails.

Project and pipeline CI/CD variables override the job's defaults, so restrict who
can set them, and protect the included template ref and baseline variables. The
existing SARIF template remains available. Test this include in the actual runner
environment before making it required.
