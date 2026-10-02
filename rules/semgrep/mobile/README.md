# Mobile Semgrep rules

Semgrep rules for static security review of mobile applications: native
Android (Java, Kotlin, `AndroidManifest.xml`, Gradle), native iOS (Swift,
Objective-C, `Info.plist`, Xcode project files), React Native / Expo, and
Flutter / Dart.

The rules flag code and configuration that commonly lead to mobile security
issues: weak cryptography, disabled TLS validation, insecure WebView settings,
exported components, sensitive data in logs or plain storage, injection sinks,
weak biometric and Keychain configuration, and missing release hardening. Most
checks are mapped to the [OWASP MASVS / MASTG](https://mas.owasp.org/) controls
and CWE identifiers in their `metadata`.

## Coverage

| Platform | Rules | Categories |
| :--- | ---: | :--- |
| Android | 233 | architecture, authentication, code, cryptography, network, platform, resilience, storage |
| iOS | 32 | authentication, code, cryptography, network, platform, storage |
| React Native / Expo | 32 | authentication, code, configuration, network, platform, storage |
| Flutter / Dart | 23 | code, cryptography, network, resilience, storage |
| **Total** | **320** | |

## Layout

```text
mobile_custom/
├── rules/
│   ├── android/<category>/*.yaml
│   ├── ios/<category>/*.yaml
│   ├── react-native/<category>/*.yaml
│   └── flutter/<category>/*.yaml
├── tests/            Test cases; mirrors the rules/ tree
├── licenses/         License texts of the upstream projects
├── LICENSE           GNU GPL v3.0
└── NOTICE.md         Origin and license of every rule group
```

## Usage

Install [Semgrep](https://semgrep.dev/docs/getting-started/quickstart/)
(`pip install semgrep` or `brew install semgrep`). The commands below run from
the repository root.

Scan an application with every rule:

```bash
semgrep scan --metrics=off --config rules/semgrep/mobile/rules/ path/to/app
```

Scan one platform, or one category inside a platform:

```bash
semgrep scan --config rules/semgrep/mobile/rules/android/ path/to/android-app
semgrep scan --config rules/semgrep/mobile/rules/ios/ path/to/ios-app
semgrep scan --config rules/semgrep/mobile/rules/react-native/ path/to/rn-app
semgrep scan --config rules/semgrep/mobile/rules/flutter/ path/to/flutter-app
semgrep scan --config rules/semgrep/mobile/rules/android/cryptography/ path/to/android-app
```

Useful options:

| Option | Effect |
| :--- | :--- |
| `--severity ERROR` | Report only high-severity findings. Repeat the flag to add `WARNING` or `INFO`. |
| `--sarif -o semgrep.sarif` | Write SARIF for GitHub code scanning, DefectDojo, or other tools. |
| `--json -o semgrep.json` | Write machine-readable JSON. |
| `--error` | Exit with a non-zero status when there are findings. Use it to fail a CI job. |
| `--exclude-rule <rule-id>` | Skip a rule that does not fit the project. |

Semgrep skips paths such as `test/`, `tests/`, and `node_modules/` by default.
Add a `.semgrepignore` file to the scanned project to change that.

### GitHub Actions

```yaml
name: mobile-semgrep
on: [pull_request]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    container: semgrep/semgrep
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: 1ega/devsecopsforall
          path: .devsecopsforall
      - run: >
          semgrep scan --metrics=off
          --config .devsecopsforall/rules/semgrep/mobile/rules/
          --sarif -o semgrep.sarif --error .
```

Pin the second checkout to a tag or commit (`ref:`) so that rule updates do not
change CI results unexpectedly.

## Reading the results

Each finding is a starting point for manual review, not proof of a
vulnerability. Several rules deliberately favor coverage over precision and
can report false positives. Check whether attacker-controlled data reaches the
flagged code, and whether the behavior is required. A clean scan does not show
that an application is secure.

Rule `metadata` carries the context needed for triage: `cwe`, `owasp-mobile` or
`masvs`, `confidence`, `references`, and the rule's `source` and `license`.

Known limitations:

- `MSTG-ARCH-9` (enforced updates) cannot read `AndroidManifest.xml` and the
  Java code together. It reports every Activity that does not start an
  in-app update flow, so only the launcher activity's finding is relevant.
- The `flutter.apiiro.*` obfuscation rules are heuristics meant to spot
  suspicious or malicious Dart code, not ordinary vulnerabilities.

## Testing

Run the test suite after changing any rule:

```bash
cd rules/semgrep/mobile
semgrep scan --test --config rules/semgrep/python/ tests/
semgrep scan --validate --config rules/
```

The test for `rules/<platform>/<category>/<name>.yaml` lives in
`tests/<platform>/<category>/<name>.<ext>`. Test files mark expected results
with comments on the line before the code:

```java
// ruleid: android.local.example-rule
webView.getSettings().setAllowFileAccess(true);

// ok: android.local.example-rule
webView.getSettings().setAllowFileAccess(false);
```

## Adding a rule

1. Put the rule in `rules/<platform>/<category>/<name>.yaml`. Use an existing
   category when one fits.
2. Give it a unique ID that starts with the platform, for example
   `android.local.webview-file-access` or `ios.local.keychain-always`.
3. Write a `message` that explains the risk and the safer alternative.
4. Set `severity`: `ERROR` for a likely exploitable issue, `WARNING` for a
   probable weakness, `INFO` for an item to review.
5. Fill in `metadata`. Include at least `category: security`, `cwe`,
   `confidence`, `references`, and `license`. Map the rule to an OWASP MASVS
   control when one applies.
6. Add a test file with at least one `ruleid:` case and one `ok:` case.
7. Run the tests and the validation commands above. Update the coverage table
   in this README if the rule count changes.
8. If the rule is derived from another project, keep its original author and
   license fields, add the project to [NOTICE.md](NOTICE.md), and add its
   license text to `licenses/` when the license requires it. Only contribute
   rules and test code that you have the right to share.

A minimal rule:

```yaml
rules:
  - id: android.local.webview-file-access
    languages: [java, kotlin]
    severity: WARNING
    message: >-
      WebView file access is enabled. A page loaded in the WebView may read
      local files. Call setAllowFileAccess(false) unless file access is required.
    metadata:
      category: security
      cwe: "CWE-200: Exposure of Sensitive Information to an Unauthorized Actor"
      masvs: MASVS-PLATFORM-2
      confidence: HIGH
      references:
        - https://developer.android.com/reference/android/webkit/WebSettings#setAllowFileAccess(boolean)
      license: GPL-3.0
    pattern: $SETTINGS.setAllowFileAccess(true)
```

## License

The rule set is distributed under the [GNU General Public License v3.0](LICENSE).
Individual rule groups also keep their original licenses (LGPL-3.0, MIT,
CC BY-SA 4.0). [NOTICE.md](NOTICE.md) lists the origin and license of each group.
