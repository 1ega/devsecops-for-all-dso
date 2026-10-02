# GitLab CI

A CI template that a project enables with a single `include:`. It mirrors the GitHub Actions workflow: the same stages, switches, and artifact names.

Expected usage:

```yaml
include:
  - project: '<group>/devsecopsforall'
    ref: v1
    file: '/integrations/gitlab-ci/security.yml'

variables:
  DSO_SEMGREP: "true"
  DSO_SECRETS: "true"
  DSO_SCA: "true"
  DSO_PROFILE: "ci-blocking"
```

Open questions:

- Run alongside GitLab's built-in Security templates, or replace them?
- Which report format to emit for the GitLab Security Dashboard on Ultimate.

**Status:** Structure only; no template is published yet.
