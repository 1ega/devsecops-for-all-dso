# CI/CD

Controls for the pipelines themselves, which hold secrets and reach production: script injection through untrusted variables, unpinned actions and images, secrets printed to logs, `allow_failure` on security jobs, and overly broad tokens. A settings checklist for GitHub and GitLab (protected branches, required reviews, protected variables, runners) belongs here too.

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| zizmor | [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) | Static analysis for GitHub Actions |
| poutine | [boostsecurityio/poutine](https://github.com/boostsecurityio/poutine) | GitHub Actions and GitLab CI |
| actionlint | [rhysd/actionlint](https://github.com/rhysd/actionlint) | GitHub Actions linter |
| Legitify | [Legit-Labs/legitify](https://github.com/Legit-Labs/legitify) | GitHub and GitLab organization settings |
| OpenSSF Scorecard | [ossf/scorecard](https://github.com/ossf/scorecard) | Repository security practices score |

Related skill: [zizmor](../../skills/cicd-iac-security/zizmor/SKILL.md).

**Status:** Structure only; no policies are published yet.
