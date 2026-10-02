# dso

A planned command-line entry point that detects a project's stack and runs the matching checks from this repository, locally or in CI.

```bash
dso scan ./app                # detect the stack and run the relevant checks
dso scan mobile ./app         # mobile checks only
dso scan --profile audit .    # full audit
dso report --format sarif     # combined report
dso upload defectdojo         # send results to DefectDojo
```

Stack detection:

| Marker | Stack |
| :--- | :--- |
| `build.gradle(.kts)`, `AndroidManifest.xml` | Android |
| `Podfile`, `*.xcodeproj`, `Package.swift` | iOS |
| `package.json` with `react-native` or `expo` | React Native |
| `pubspec.yaml` | Flutter |
| `*.tf`, `Chart.yaml` | Infrastructure as code |
| `Dockerfile` | Containers |

Open questions:

- Implementation language: Bash or Make (fewest dependencies), Python, or Go (single binary).
- Run tools from the host, or from one container image with every tool pinned.

**Status:** Design only; no code is published yet.
