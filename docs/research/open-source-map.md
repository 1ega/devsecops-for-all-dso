# Research: open-source map

**Date:** 2026-10-02
**Target directories:** all sections

A survey of 96 open-source projects that can fill the sections of this repository, grouped by area. For every project: its role, license, activity, and — where content was imported — the directory that now holds it. Imported content keeps its upstream license; see [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).

Programs and installers were not copied. Only reusable content — rules, policies, templates, standards, guides, and skills — was imported, and only when the license allows redistribution.

Stars and activity reflect the state on the survey date. Security notes come from the original survey and should be re-checked before relying on a tool.

## Areas

| Area | Coverage | Summary |
| :--- | :--- | :--- |
| [Mobile: secrets](#secrets) | Partly covered | The engines are ready. No ready-made rules found for google-services.json, GoogleService-Info.plist, *.jks, keystore.properties, or fastlane/Appfile — write our own. |
| [Mobile: dependencies (SCA)](#sca) | Partly covered | Trivy reads all four mobile lockfiles. No ready-made policies for banned or abandoned SDKs. |
| [Mobile: APK/IPA build analysis](#build) | Ready to use | MobSF for built APK/IPA files, mobsfscan for source code, SARIF output. |
| [Mobile: build rules and configuration](#cfg) | Write our own | MASTG rules cover part of it. No dedicated project found for network_security_config, R8/ProGuard, signing files in the repo, or Expo EAS. |
| [Backend SAST](#sast) | Ready to use | Semgrep or Opengrep plus specialized tools: find-sec-bugs (Java), gosec (Go), eslint-plugin-security (JS/TS). |
| [CI/CD security](#cicd) | Partly covered | Only poutine and Checkov are mature for GitLab CI. zizmor, actionlint, pinact, and harden-runner work only with GitHub Actions. |
| [Infrastructure as code](#iac) | Ready to use | Checkov (custom policies in Python/YAML), KICS (Rego), Conftest/OPA. |
| [Containers](#cont) | Partly covered | Linters and minimal images exist. No maintained set of hardened reference Dockerfiles found. |
| [Kubernetes policies](#k8s) | Ready to use | Kyverno and Gatekeeper policy libraries; policy tests with Chainsaw. |
| [Supply chain: SBOM, signing, SLSA](#supply) | Ready to use | For GitLab: keyless cosign via OIDC and witness (has a GitLab attestor). slsa-github-generator works only with GitHub Actions. |
| [Dynamic testing](#dast) | Ready to use | ZAP baseline/API scans, nuclei with custom templates, Schemathesis for OpenAPI. |
| [Standards and mapping](#std) | Partly covered | MASVS, MASTG, ASVS, and OpenCRE exist. No ready-made rule → PCI DSS 4.0 table found. |
| [Threat modeling (STRIDE)](#tm) | Partly covered | Tools exist. No templates found for mobile login, biometrics, payments, or deep links. |
| [Claude Code and AI skills](#ai) | Partly covered | Semgrep rule generation and SARIF analysis exist in trailofbits/skills. No skill found for MobSF reports. |
| [Result orchestration](#glue) | Ready to use | DefectDojo and secureCodeBox ingest scanner results; SARIF is the common format. |

<a id="secrets"></a>

## Mobile: secrets

**Coverage:** Partly covered. The engines are ready. No ready-made rules found for google-services.json, GoogleService-Info.plist, *.jks, keystore.properties, or fastlane/Appfile — write our own.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) **(core)** | Successor to gitleaks by its author. Reads .gitleaks.toml, rules with CEL validation, pure Go. | MIT | active (last push 2026-09-30) | 2,083 | — |
| [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) **(core)** | Custom rules in TOML ([extend] useDefault), composite rules since v8.28.0, pre-commit hook and Action. *Note: The author has stated he lost full control of the repository.* | MIT | active (last push 2026-09-30) | 29,608 | [`scanners/gitleaks/default-config/`](../../scanners/gitleaks/default-config/SOURCE.md) |
| [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | Finds, verifies, and analyzes leaked credentials. | AGPL-3.0 | active (last push 2026-10-01) | 28,239 | — |
| [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) | Enterprise approach with a baseline file of known findings. | Apache-2.0 | slow (last push 2026-04-02) | 4,647 | — |
| [dwisiswant0/apkleaks](https://github.com/dwisiswant0/apkleaks) | Finds URIs, endpoints, and secrets in a built APK. *Note: Last activity August 2025.* | Apache-2.0 | stale (last push 2025-08-20) | 6,328 | [`scanners/apkleaks/`](../../scanners/apkleaks/SOURCE.md) |
| [mazen160/secrets-patterns-db](https://github.com/mazen160/secrets-patterns-db) | The largest open database of patterns for keys, tokens, and passwords — raw material for custom rules. | CC-BY-SA-4.0 | stale (last push 2025-08-06) | 1,618 | [`scanners/secrets-patterns-db/`](../../scanners/secrets-patterns-db/SOURCE.md) |
| [praetorian-inc/noseyparker](https://github.com/praetorian-inc/noseyparker) | Secret detection in text and git history. | Apache-2.0 | archived (last push 2026-02-21) | 2,340 | — |
| [Skyscanner/whispers](https://github.com/Skyscanner/whispers) | Secret detection in code and configuration. | Apache-2.0 | archived (last push 2023-10-11) | 506 | — |

<a id="sca"></a>

## Mobile: dependencies (SCA)

**Coverage:** Partly covered. Trivy reads all four mobile lockfiles. No ready-made policies for banned or abandoned SDKs.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) **(core)** | Per its documentation, reads gradle.lockfile, pubspec.lock, Podfile.lock, Package.resolved, npm/yarn/pnpm. Also images, IaC, SBOM. *Note: March 2026: trivy-action, setup-trivy, and Docker Hub images were compromised — pin by digest and verify.* | Apache-2.0 | active (last push 2026-10-02) | 38,186 | — |
| [google/osv-scanner](https://github.com/google/osv-scanner) **(core)** | Reads gradle.lockfile, pubspec.lock, npm. Podfile.lock and Package.resolved are not in the official support table. Offline mode and experimental flagging of deprecated packages. | Apache-2.0 | active (last push 2026-10-02) | 11,133 | — |
| [anchore/syft](https://github.com/anchore/syft) | SBOM generation from images and filesystems. | Apache-2.0 | active (last push 2026-10-01) | 9,632 | — |
| [anchore/grype](https://github.com/anchore/grype) | Vulnerability scanning of an image or SBOM. | Apache-2.0 | active (last push 2026-10-01) | 12,967 | — |
| [cdxgen/cdxgen](https://github.com/cdxgen/cdxgen) | CycloneDX BOMs from source code and images, many languages. | Apache-2.0 | active (last push 2026-10-02) | 1,082 | — |
| [dependency-check/DependencyCheck](https://github.com/dependency-check/DependencyCheck) | OWASP SCA for Java/Gradle and other ecosystems. | Apache-2.0 | active (last push 2026-10-02) | 7,715 | — |
| [ossf/scorecard](https://github.com/ossf/scorecard) | Security metrics for open-source dependencies and repositories. | Apache-2.0 | active (last push 2026-10-02) | 5,732 | — |
| [DependencyTrack/dependency-track](https://github.com/DependencyTrack/dependency-track) | Platform for continuous SBOM analysis. | Apache-2.0 | active (last push 2026-10-02) | 4,259 | — |

<a id="build"></a>

## Mobile: APK/IPA build analysis

**Coverage:** Ready to use. MobSF for built APK/IPA files, mobsfscan for source code, SARIF output.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [dwisiswant0/apkleaks](https://github.com/dwisiswant0/apkleaks) | Finds URIs, endpoints, and secrets in a built APK. *Note: Last activity August 2025.* | Apache-2.0 | stale (last push 2025-08-20) | 6,328 | [`scanners/apkleaks/`](../../scanners/apkleaks/SOURCE.md) |
| [MobSF/Mobile-Security-Framework-MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) **(core)** | Static and dynamic analysis of APK/IPA files, API fuzzing. | GPL-3.0 | active (last push 2026-09-30) | 21,867 | — |
| [MobSF/mobsfscan](https://github.com/MobSF/mobsfscan) **(core)** | Android/iOS source SAST: Java, Kotlin, Android XML, Info.plist, Swift, Objective-C. Output: SARIF 2.1.0, GitLab SAST, SonarQube, JSON, HTML. | LGPL-3.0 | active (last push 2026-09-21) | 791 | — |
| [skylot/jadx](https://github.com/skylot/jadx) | Decompiles APK/DEX to Java — input for Semgrep rules on decompiled code. | Apache-2.0 | active (last push 2026-10-01) | 50,708 | — |
| [iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool) | Unpacks APK resources and the manifest. | Apache-2.0 | active (last push 2026-09-28) | 25,716 | — |
| [androguard/androguard](https://github.com/androguard/androguard) | Python analysis of APK/DEX. | Apache-2.0 | active (last push 2026-10-02) | 6,313 | — |

<a id="cfg"></a>

## Mobile: build rules and configuration

**Coverage:** Write our own. MASTG rules cover part of it. No dedicated project found for network_security_config, R8/ProGuard, signing files in the repo, or Expo EAS.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [MobSF/mobsfscan](https://github.com/MobSF/mobsfscan) **(core)** | Android/iOS source SAST: Java, Kotlin, Android XML, Info.plist, Swift, Objective-C. Output: SARIF 2.1.0, GitLab SAST, SonarQube, JSON, HTML. | LGPL-3.0 | active (last push 2026-09-21) | 791 | — |
| [OWASP/mastg](https://github.com/OWASP/mastg) **(core)** | Tests and demos; rules/ holds Semgrep rules whose messages start with a MASVS identifier. | CC-BY-SA-4.0 | active (last push 2026-10-01) | 13,216 | [`guides/owasp-mastg/`](../../guides/owasp-mastg/SOURCE.md) |
| [OWASP/masvs](https://github.com/OWASP/masvs) | Security requirements standard for mobile applications. | CC-BY-SA-4.0 | active (last push 2026-09-21) | 2,456 | [`reporting/compliance-mapping/masvs/`](../../reporting/compliance-mapping/masvs/SOURCE.md) |
| [mindedsecurity/semgrep-rules-android-security](https://github.com/mindedsecurity/semgrep-rules-android-security) | Semgrep rules following MASTG for Android; status.md rates each rule's maturity by MASVS ID. Designed for decompiled code. | GPL-3.0 | slow (last push 2026-06-05) | 340 | — |
| [insideapp-fr/mobile-application-security-rules](https://github.com/insideapp-fr/mobile-application-security-rules) | Semgrep rules following MASTG: iOS (Swift) and Android (Java, Kotlin), with tests. *Note: Last push August 2023; no license file.* | none | stale (last push 2023-08-24) | 7 | — |

<a id="sast"></a>

## Backend SAST

**Coverage:** Ready to use. Semgrep or Opengrep plus specialized tools: find-sec-bugs (Java), gosec (Go), eslint-plugin-security (JS/TS).

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [semgrep/semgrep](https://github.com/semgrep/semgrep) **(core)** | Static analysis engine, LGPL-2.1. | LGPL-2.1 | active (last push 2026-10-02) | 16,837 | — |
| [semgrep/semgrep-rules](https://github.com/semgrep/semgrep-rules) **(core)** | Official community rules under the Semgrep Rules License. *Note: Check the license terms before shipping these rules in a distributed product.* | NOASSERTION | active (last push 2026-09-28) | 1,261 | — |
| [opengrep/opengrep](https://github.com/opengrep/opengrep) | Fork of the Semgrep engine under LGPL-2.1; the separate opengrep-rules repository is archived. | LGPL-2.1 | active (last push 2026-10-01) | 3,131 | — |
| [find-sec-bugs/find-sec-bugs](https://github.com/find-sec-bugs/find-sec-bugs) | Security rules for Java (SpotBugs plugin). | LGPL-3.0 | slow (last push 2026-03-26) | 2,449 | — |
| [securego/gosec](https://github.com/securego/gosec) | Security scanner for Go. | Apache-2.0 | active (last push 2026-10-02) | 8,961 | — |
| [eslint-community/eslint-plugin-security](https://github.com/eslint-community/eslint-plugin-security) | ESLint security rules for JS/TS. | Apache-2.0 | active (last push 2026-10-01) | 2,379 | — |
| [trailofbits/semgrep-rules](https://github.com/trailofbits/semgrep-rules) | Semgrep rules from Trail of Bits. *Note: AGPL-3.0.* | AGPL-3.0 | slow (last push 2026-05-07) | 531 | [`semgrep-rules/trailofbits/`](../../semgrep-rules/trailofbits/SOURCE.md) |
| [elttam/semgrep-rules](https://github.com/elttam/semgrep-rules) | Additional Semgrep rules, MIT. | MIT | active (last push 2026-09-28) | 246 | [`semgrep-rules/elttam/`](../../semgrep-rules/elttam/SOURCE.md) |
| [github/codeql](https://github.com/github/codeql) | CodeQL query libraries. *Note: Check the CodeQL CLI terms of use.* | MIT | active (last push 2026-10-02) | 10,155 | — |

<a id="cicd"></a>

## CI/CD security

**Coverage:** Partly covered. Only poutine and Checkov are mature for GitLab CI. zizmor, actionlint, pinact, and harden-runner work only with GitHub Actions.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [ossf/scorecard](https://github.com/ossf/scorecard) | Security metrics for open-source dependencies and repositories. | Apache-2.0 | active (last push 2026-10-02) | 5,732 | — |
| [boostsecurityio/poutine](https://github.com/boostsecurityio/poutine) **(core)** | GitHub Actions, GitLab CI, Azure DevOps, Tekton. Custom Rego rules, SARIF, inventory of build dependencies. | Apache-2.0 | active (last push 2026-07-09) | 523 | [`policies/cicd/poutine-rego/`](../../policies/cicd/poutine-rego/SOURCE.md) |
| [bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) **(core)** | Frameworks: gitlab_ci, github_actions, dockerfile, helm, kubernetes, secrets, terraform. Custom policies in Python and YAML. | Apache-2.0 | active (last push 2026-10-01) | 9,049 | — |
| [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) | Static analysis of GitHub Actions (GitHub only). | MIT | active (last push 2026-10-02) | 6,623 | — |
| [rhysd/actionlint](https://github.com/rhysd/actionlint) | Linter for GitHub Actions workflow files. | MIT | active (last push 2026-07-16) | 4,286 | — |
| [suzuki-shunsuke/pinact](https://github.com/suzuki-shunsuke/pinact) | Pins GitHub Actions versions to SHAs. | MIT | active (last push 2026-10-01) | 1,216 | — |
| [stacklok/frizbee](https://github.com/stacklok/frizbee) | Pins Actions and images to checksums. | Apache-2.0 | active (last push 2026-10-01) | 186 | — |
| [step-security/harden-runner](https://github.com/step-security/harden-runner) | Runtime protection for GitHub-hosted runners. | Apache-2.0 | active (last push 2026-09-30) | 1,278 | — |

<a id="iac"></a>

## Infrastructure as code

**Coverage:** Ready to use. Checkov (custom policies in Python/YAML), KICS (Rego), Conftest/OPA.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) **(core)** | Per its documentation, reads gradle.lockfile, pubspec.lock, Podfile.lock, Package.resolved, npm/yarn/pnpm. Also images, IaC, SBOM. *Note: March 2026: trivy-action, setup-trivy, and Docker Hub images were compromised — pin by digest and verify.* | Apache-2.0 | active (last push 2026-10-02) | 38,186 | — |
| [bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) **(core)** | Frameworks: gitlab_ci, github_actions, dockerfile, helm, kubernetes, secrets, terraform. Custom policies in Python and YAML. | Apache-2.0 | active (last push 2026-10-01) | 9,049 | — |
| [Checkmarx/kics](https://github.com/Checkmarx/kics) | Rego queries for Terraform, Helm, Docker, and more. *Note: March–April 2026: GitHub Actions and Docker Hub images were compromised — pin by digest and verify.* | Apache-2.0 | active (last push 2026-10-01) | 2,712 | — |
| [open-policy-agent/conftest](https://github.com/open-policy-agent/conftest) **(core)** | Rego tests for configuration files. | NOASSERTION | active (last push 2026-10-01) | 3,275 | [`policies/terraform/conftest-examples/`](../../policies/terraform/conftest-examples/SOURCE.md) |
| [open-policy-agent/opa](https://github.com/open-policy-agent/opa) | Rego policy engine. | Apache-2.0 | active (last push 2026-10-02) | 12,304 | — |
| [terraform-compliance/cli](https://github.com/terraform-compliance/cli) | BDD checks of terraform plan. | MIT | active (last push 2026-09-07) | 1,463 | — |
| [aquasecurity/tfsec](https://github.com/aquasecurity/tfsec) | Terraform scanner; little activity. | MIT | slow (last push 2026-03-25) | 7,042 | — |
| [tenable/terrascan](https://github.com/tenable/terrascan) | IaC scanner. | Apache-2.0 | archived (last push 2025-11-20) | 5,215 | — |
| [stackrox/kube-linter](https://github.com/stackrox/kube-linter) | Linter for Kubernetes manifests and Helm charts. | Apache-2.0 | active (last push 2026-09-30) | 3,517 | — |

<a id="cont"></a>

## Containers

**Coverage:** Partly covered. Linters and minimal images exist. No maintained set of hardened reference Dockerfiles found.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) **(core)** | Per its documentation, reads gradle.lockfile, pubspec.lock, Podfile.lock, Package.resolved, npm/yarn/pnpm. Also images, IaC, SBOM. *Note: March 2026: trivy-action, setup-trivy, and Docker Hub images were compromised — pin by digest and verify.* | Apache-2.0 | active (last push 2026-10-02) | 38,186 | — |
| [hadolint/hadolint](https://github.com/hadolint/hadolint) **(core)** | Dockerfile linter. | GPL-3.0 | active (last push 2026-09-25) | 12,448 | — |
| [goodwithtech/dockle](https://github.com/goodwithtech/dockle) **(core)** | Image linter following best practices. | Apache-2.0 | active (last push 2026-08-10) | 3,297 | — |
| [docker/docker-bench-security](https://github.com/docker/docker-bench-security) | CIS checks for a Docker host. | Apache-2.0 | slow (last push 2026-06-04) | 9,702 | — |
| [GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless) | Minimal base images without a shell or package manager. | Apache-2.0 | active (last push 2026-10-01) | 23,114 | [`policies/containers/distroless-examples/`](../../policies/containers/distroless-examples/SOURCE.md) |
| [wolfi-dev/os](https://github.com/wolfi-dev/os) | Wolfi: a distribution for minimal images. | NOASSERTION | active (last push 2026-10-01) | 1,292 | — |
| [chainguard-dev/apko](https://github.com/chainguard-dev/apko) | Reproducible image builds from APK packages. | Apache-2.0 | active (last push 2026-10-01) | 1,685 | — |
| [slimtoolkit/slim](https://github.com/slimtoolkit/slim) | Reduces image size. | Apache-2.0 | active (last push 2026-09-19) | 23,422 | — |
| [dnaprawa/dockerfile-best-practices](https://github.com/dnaprawa/dockerfile-best-practices) | Collection of Dockerfile tips. *Note: Last activity 2021; no license, so content cannot be copied.* | none | stale (last push 2021-07-29) | 253 | — |

<a id="k8s"></a>

## Kubernetes policies

**Coverage:** Ready to use. Kyverno and Gatekeeper policy libraries; policy tests with Chainsaw.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [open-policy-agent/opa](https://github.com/open-policy-agent/opa) | Rego policy engine. | Apache-2.0 | active (last push 2026-10-02) | 12,304 | — |
| [stackrox/kube-linter](https://github.com/stackrox/kube-linter) | Linter for Kubernetes manifests and Helm charts. | Apache-2.0 | active (last push 2026-09-30) | 3,517 | — |
| [kyverno/kyverno](https://github.com/kyverno/kyverno) **(core)** | Admission controller with policies as YAML. | Apache-2.0 | active (last push 2026-10-02) | 8,211 | — |
| [kyverno/policies](https://github.com/kyverno/policies) **(core)** | Ready-made library of Kyverno policies. | Apache-2.0 | active (last push 2026-10-02) | 501 | [`policies/kubernetes/kyverno-policies/`](../../policies/kubernetes/kyverno-policies/SOURCE.md) |
| [kyverno/chainsaw](https://github.com/kyverno/chainsaw) | Tests for Kyverno policies and manifests. | Apache-2.0 | active (last push 2026-09-03) | 622 | — |
| [open-policy-agent/gatekeeper](https://github.com/open-policy-agent/gatekeeper) **(core)** | Admission controller built on OPA. | Apache-2.0 | active (last push 2026-09-30) | 4,289 | — |
| [open-policy-agent/gatekeeper-library](https://github.com/open-policy-agent/gatekeeper-library) **(core)** | Ready-made library of Gatekeeper policies. | Apache-2.0 | active (last push 2026-09-28) | 704 | [`policies/kubernetes/gatekeeper-library/`](../../policies/kubernetes/gatekeeper-library/SOURCE.md) |
| [kubescape/kubescape](https://github.com/kubescape/kubescape) | Kubernetes scanner against security frameworks. | Apache-2.0 | active (last push 2026-10-02) | 11,761 | — |
| [aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench) | CIS checks for a cluster. | Apache-2.0 | active (last push 2026-10-01) | 8,208 | — |
| [Shopify/kubeaudit](https://github.com/Shopify/kubeaudit) | Kubernetes cluster audit. | MIT | archived (last push 2024-08-21) | 1,936 | — |
| [sigstore/policy-controller](https://github.com/sigstore/policy-controller) | Admission-time signature verification in the cluster. | NOASSERTION | active (last push 2026-09-28) | 182 | [`policies/supply-chain/sigstore-policy-controller/`](../../policies/supply-chain/sigstore-policy-controller/SOURCE.md) |

<a id="supply"></a>

## Supply chain: SBOM, signing, SLSA

**Coverage:** Ready to use. For GitLab: keyless cosign via OIDC and witness (has a GitLab attestor). slsa-github-generator works only with GitHub Actions.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [aquasecurity/trivy](https://github.com/aquasecurity/trivy) **(core)** | Per its documentation, reads gradle.lockfile, pubspec.lock, Podfile.lock, Package.resolved, npm/yarn/pnpm. Also images, IaC, SBOM. *Note: March 2026: trivy-action, setup-trivy, and Docker Hub images were compromised — pin by digest and verify.* | Apache-2.0 | active (last push 2026-10-02) | 38,186 | — |
| [anchore/syft](https://github.com/anchore/syft) | SBOM generation from images and filesystems. | Apache-2.0 | active (last push 2026-10-01) | 9,632 | — |
| [cdxgen/cdxgen](https://github.com/cdxgen/cdxgen) | CycloneDX BOMs from source code and images, many languages. | Apache-2.0 | active (last push 2026-10-02) | 1,082 | — |
| [DependencyTrack/dependency-track](https://github.com/DependencyTrack/dependency-track) | Platform for continuous SBOM analysis. | Apache-2.0 | active (last push 2026-10-02) | 4,259 | — |
| [sigstore/cosign](https://github.com/sigstore/cosign) **(core)** | Signs and verifies images and artifacts; keyless via OIDC, including from GitLab CI. | Apache-2.0 | active (last push 2026-10-01) | 6,344 | — |
| [in-toto/witness](https://github.com/in-toto/witness) **(core)** | Build attestations; has a GitLab attestor, keyless via Sigstore and SPIFFE. | Apache-2.0 | active (last push 2026-09-28) | 547 | — |
| [slsa-framework/slsa-github-generator](https://github.com/slsa-framework/slsa-github-generator) | SLSA provenance; works only with GitHub Actions. | Apache-2.0 | active (last push 2026-08-07) | 601 | — |
| [slsa-framework/slsa-verifier](https://github.com/slsa-framework/slsa-verifier) | Verifies SLSA provenance. | Apache-2.0 | active (last push 2026-08-07) | 347 | — |
| [sigstore/policy-controller](https://github.com/sigstore/policy-controller) | Admission-time signature verification in the cluster. | NOASSERTION | active (last push 2026-09-28) | 182 | [`policies/supply-chain/sigstore-policy-controller/`](../../policies/supply-chain/sigstore-policy-controller/SOURCE.md) |
| [interlynk-io/sbomqs](https://github.com/interlynk-io/sbomqs) | SBOM quality scoring. | Apache-2.0 | active (last push 2026-10-02) | 308 | — |

<a id="dast"></a>

## Dynamic testing

**Coverage:** Ready to use. ZAP baseline/API scans, nuclei with custom templates, Schemathesis for OpenAPI.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [zaproxy/zaproxy](https://github.com/zaproxy/zaproxy) **(core)** | DAST engine; baseline and API scans. | Apache-2.0 | active (last push 2026-10-01) | 15,856 | — |
| [zaproxy/action-baseline](https://github.com/zaproxy/action-baseline) | GitHub Action for the ZAP baseline scan. | Apache-2.0 | active (last push 2026-09-06) | 371 | — |
| [zaproxy/action-api-scan](https://github.com/zaproxy/action-api-scan) | GitHub Action for the ZAP API scan. | Apache-2.0 | active (last push 2026-09-07) | 77 | — |
| [zaproxy/community-scripts](https://github.com/zaproxy/community-scripts) | Community scripts for ZAP. | Apache-2.0 | active (last push 2026-10-01) | 897 | [`scanners/zap/community-scripts/`](../../scanners/zap/community-scripts/SOURCE.md) |
| [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) **(core)** | Scanner driven by YAML templates; convenient for writing templates for your own APIs. | MIT | active (last push 2026-10-01) | 31,673 | — |
| [projectdiscovery/nuclei-templates](https://github.com/projectdiscovery/nuclei-templates) **(core)** | Community library of nuclei templates. | MIT | active (last push 2026-10-02) | 13,049 | — |
| [projectdiscovery/fuzzing-templates](https://github.com/projectdiscovery/fuzzing-templates) | nuclei templates for fuzzing. | MIT | archived (last push 2024-05-02) | 108 | [`scanners/nuclei/fuzzing-templates/`](../../scanners/nuclei/fuzzing-templates/SOURCE.md) |
| [schemathesis/schemathesis](https://github.com/schemathesis/schemathesis) **(core)** | Property-based API testing from OpenAPI/GraphQL schemas. | MIT | active (last push 2026-10-02) | 3,644 | — |
| [microsoft/restler-fuzzer](https://github.com/microsoft/restler-fuzzer) | Stateful REST API fuzzing. | MIT | slow (last push 2026-06-10) | 2,950 | — |

<a id="std"></a>

## Standards and mapping

**Coverage:** Partly covered. MASVS, MASTG, ASVS, and OpenCRE exist. No ready-made rule → PCI DSS 4.0 table found.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [OWASP/mastg](https://github.com/OWASP/mastg) **(core)** | Tests and demos; rules/ holds Semgrep rules whose messages start with a MASVS identifier. | CC-BY-SA-4.0 | active (last push 2026-10-01) | 13,216 | [`guides/owasp-mastg/`](../../guides/owasp-mastg/SOURCE.md) |
| [OWASP/masvs](https://github.com/OWASP/masvs) | Security requirements standard for mobile applications. | CC-BY-SA-4.0 | active (last push 2026-09-21) | 2,456 | [`reporting/compliance-mapping/masvs/`](../../reporting/compliance-mapping/masvs/SOURCE.md) |
| [OWASP/ASVS](https://github.com/OWASP/ASVS) **(core)** | Application Security Verification Standard. | CC-BY-SA-4.0 | active (last push 2026-09-24) | 3,643 | [`reporting/compliance-mapping/asvs-5.0/`](../../reporting/compliance-mapping/asvs-5.0/SOURCE.md) |
| [OWASP/OpenCRE](https://github.com/OWASP/OpenCRE) | Maps requirements of different standards to each other. | CC0-1.0 | active (last push 2026-10-02) | 188 | — |
| [OWASP/CheatSheetSeries](https://github.com/OWASP/CheatSheetSeries) | Remediation examples for triage playbooks. | CC-BY-SA-4.0 | active (last push 2026-10-02) | 33,380 | [`guides/owasp-cheatsheets/`](../../guides/owasp-cheatsheets/SOURCE.md) |
| [prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | Cloud audit with ready-made compliance frameworks. | Apache-2.0 | active (last push 2026-10-01) | 14,913 | [`reporting/compliance-mapping/prowler/`](../../reporting/compliance-mapping/prowler/SOURCE.md) |
| [ComplianceAsCode/content](https://github.com/ComplianceAsCode/content) | Compliance profiles and hardening as code. | NOASSERTION | active (last push 2026-10-02) | 2,814 | — |
| [oscal-compass/compliance-trestle](https://github.com/oscal-compass/compliance-trestle) | OSCAL tooling for compliance as code. | Apache-2.0 | active (last push 2026-09-30) | 282 | — |

<a id="tm"></a>

## Threat modeling (STRIDE)

**Coverage:** Partly covered. Tools exist. No templates found for mobile login, biometrics, payments, or deep links.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [OWASP/pytm](https://github.com/OWASP/pytm) **(core)** | Threat model as Python code. | NOASSERTION | active (last push 2026-08-19) | 1,171 | — |
| [OWASP/threat-dragon](https://github.com/OWASP/threat-dragon) **(core)** | Visual threat model editor. | Apache-2.0 | active (last push 2026-09-30) | 1,617 | — |
| [Threagile/threagile](https://github.com/Threagile/threagile) | Threat model as YAML. | MIT | slow (last push 2026-04-08) | 784 | [`templates/threat-models/threagile/`](../../templates/threat-models/threagile/SOURCE.md) |
| [threatcl/threatcl](https://github.com/threatcl/threatcl) | Threat model as HCL. | MIT | active (last push 2026-09-27) | 466 | [`templates/threat-models/threatcl/`](../../templates/threat-models/threatcl/SOURCE.md) |
| [OWASP/threat-model-cookbook](https://github.com/OWASP/threat-model-cookbook) | Collection of example threat models. | NOASSERTION | archived (last push 2021-11-10) | 430 | [`templates/threat-models/threat-model-cookbook/`](../../templates/threat-models/threat-model-cookbook/SOURCE.md) |
| [mozilla/seasponge](https://github.com/mozilla/seasponge) | Threat model editor. | MPL-2.0 | archived (last push 2018-04-16) | 284 | — |

<a id="ai"></a>

## Claude Code and AI skills

**Coverage:** Partly covered. Semgrep rule generation and SARIF analysis exist in trailofbits/skills. No skill found for MobSF reports.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [trailofbits/skills](https://github.com/trailofbits/skills) **(core)** | Claude Code plugins: semgrep-rule-creator, semgrep-rule-variant-creator, static-analysis (CodeQL, Semgrep, SARIF parsing), variant-analysis, differential-review. | CC-BY-SA-4.0 | active (last push 2026-10-02) | 7,341 | [`skills/trailofbits/`](../../skills/trailofbits/SOURCE.md) |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | GitHub Action for AI security review of changes. | MIT | slow (last push 2026-02-11) | 6,292 | — |
| [semgrep/mcp](https://github.com/semgrep/mcp) | Semgrep MCP server. | MIT | archived (last push 2025-10-28) | 687 | — |

<a id="glue"></a>

## Result orchestration

**Coverage:** Ready to use. DefectDojo and secureCodeBox ingest scanner results; SARIF is the common format.

| Project | Role | License | Activity | Stars | In this repo |
| :--- | :--- | :--- | :--- | ---: | :--- |
| [DefectDojo/django-DefectDojo](https://github.com/DefectDojo/django-DefectDojo) **(core)** | Vulnerability management; imports scanner results. | BSD-3-Clause | active (last push 2026-10-02) | 4,976 | — |
| [secureCodeBox/secureCodeBox](https://github.com/secureCodeBox/secureCodeBox) | OWASP orchestration of scanners in Kubernetes. | NOASSERTION | active (last push 2026-10-02) | 990 | — |

## Not imported

- Program source code, installers, and binaries.
- `semgrep/semgrep-rules`: the Semgrep Rules License restricts redistribution in products; reference it instead of copying.
- `projectdiscovery/nuclei-templates`, `Checkmarx/kics` queries, `ComplianceAsCode/content`: too large to vendor and updated daily — use them from upstream.
- `dnaprawa/dockerfile-best-practices`, `insideapp-fr/mobile-application-security-rules`: no license file.
- `github/codeql`: the shallow clone failed because of its size; use the query packs from upstream.
- Prowler frameworks whose text is not in English (ENS RD2022, SecNumCloud, Korean ISMS-P).
