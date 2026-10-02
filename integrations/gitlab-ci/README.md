# GitLab CI starter scans

Copy this into the application, setting the repository path and reviewed commit:

```yaml
include:
  - project: group/devsecopsforall
    ref: FULL_COMMIT_SHA
    file: /integrations/gitlab-ci/security.yml
stages: [test]
```

The job uses stage `test`; merge it into existing stages. A dedicated runner
with a working Docker daemon, POSIX shell and registry/database network access
is required. Docker access can control the runner host: use disposable isolated
runners for untrusted merge requests, without production credentials or shared
privileged build state. Do not expose a remote Docker daemon to PR jobs.

[Template](security.yml): pinned images, read-only source, private SARIF artifacts
for seven days. Secret findings block; dependency/SAST findings are report-only;
execution errors or missing reports fail. Set `DSO_SECRETS`, `DSO_SCA`, `DSO_SAST`
to `false` only for a documented inapplicable check. Test expected findings and
scanner failures before requiring the job. See [CI hardening](../../guides/cicd-hardening.md).

Optional [infrastructure.yml](infrastructure.yml) adds a Trivy IaC job and an image job when `DSO_IMAGE_DIGEST` is set to a full immutable reference. It uses container jobs, blocks HIGH/CRITICAL and errors, and requires an appropriately isolated runner. Supply private-registry access only in protected trusted jobs.
