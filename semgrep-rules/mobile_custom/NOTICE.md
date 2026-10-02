# Notice

This rule set includes material from the projects listed below. Each rule keeps
its original authorship fields, and its `metadata.source` and
`metadata.license` fields identify where it came from. License texts are in
[`LICENSE`](LICENSE) and [`licenses/`](licenses/).

| Rule IDs | Project | Authors | License |
| :--- | :--- | :--- | :--- |
| `MSTG-*` | [mindedsecurity/semgrep-rules-android-security](https://github.com/mindedsecurity/semgrep-rules-android-security) | IMQ Minded Security: Riccardo Cardelli, Andrea Agnello, Riccardo Granata, Michele Tumolo, Maurizio Siddu, Martino Lessio, Giovanni Fazi, Giacomo Zorzin, Christian Cotignola, Michele Di | GPL-3.0 |
| `android.owasp.*`, `detect-dangerous-android-permissions` | [OWASP/mastg](https://github.com/OWASP/mastg) (commit `a1b0e11`) | OWASP MAS project contributors | [CC BY-SA 4.0](licenses/OWASP-MASTG-CC-BY-SA-4.0.md) |
| `android.mobsf.*` | [MobSF/mobsfscan](https://github.com/MobSF/mobsfscan) (commit `ec2927a`) | MobSF contributors | [LGPL-3.0](licenses/MOBSFSCAN-LGPL-3.0.txt) |
| `android.gitlab.*`, `ios.gitlab.*` | [GitLab SAST rules](https://gitlab.com/gitlab-org/security-products/sast-rules) (commit `d580ded`) | GitLab Inc.; parts derived from [find-sec-bugs](https://find-sec-bugs.github.io/) and mobsfscan | LGPL-3.0 per file header; [GitLab license](licenses/GITLAB-SAST-RULES-LICENSE.txt) |
| `ios.akabe1.*` | [akabe1/akabe1-semgrep-rules](https://github.com/akabe1/akabe1-semgrep-rules) (commit `db843f1`) | Maurizio Siddu (@akabe1) | GPL-3.0-or-later |
| `android.federicodotta.*` | [federicodotta/semgrep-rules](https://github.com/federicodotta/semgrep-rules) (commit `51b9b69`) | Federico Dotta (@apps3c), HN Security | [MIT](licenses/FEDERICODOTTA-MIT.txt) |
| `flutter.apiiro.*` | [apiiro/malicious-code-ruleset](https://github.com/apiiro/malicious-code-ruleset) (commit `a21246b`) | Apiiro | [MIT](licenses/APIIRO-MALICIOUS-CODE-MIT.txt) |
| `react-native.*` | Check scenarios adapted from [adnxy/rnsec](https://github.com/adnxy/rnsec) (commit `7035520`) and written as new Semgrep patterns | adnxy (scenarios) | GPL-3.0; scenarios under [MIT](licenses/RNSEC-MIT.txt) |
| `android.local.*`, `ios.local.*`, `flutter.*` (except `flutter.apiiro.*`) | Written for this rule set | — | GPL-3.0 |

Test files copied from these projects keep their original license headers.

## Changes from the upstream projects

- Rule IDs from OWASP MASTG, MobSF, GitLab, akabe1, federicodotta, and Apiiro
  were prefixed with the platform and project namespace so that all rules can
  be loaded together. `MSTG-*` IDs were not changed.
- `metadata.source` and `metadata.license` were added to every rule.
- `MSTG-ARCH-9` was rewritten from `mode: join` into a single Java rule,
  because join mode crashes current Semgrep releases. It now checks Activity
  subclasses for an in-app update flow without reading `AndroidManifest.xml`.
- `flutter.apiiro.dart-obfuscation-conditions`: the `switch` pattern, which
  Semgrep cannot parse for Dart, was replaced with `case` and `default`
  patterns. The line-length regex was removed so findings point at the
  condition statement, and a test file was added.
