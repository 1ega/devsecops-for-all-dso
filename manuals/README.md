# Manuals

Practical manuals for DevSecOps tools: what each tool is for, how to install and use it, a CI example where one is useful, and how to read its results. Each manual links to the tool's GitHub repository and documentation.

They are grouped in the order most teams adopt them. To write a deeper manual for a tool, start from the [template](TEMPLATE.md).

## 1. Protect your code

### Secret scanning

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [gitleaks](gitleaks.md) (start here) | [gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) | MIT |
| [TruffleHog](trufflehog.md) | [trufflesecurity/trufflehog](https://github.com/trufflesecurity/trufflehog) | AGPL-3.0 |
| [betterleaks](betterleaks.md) | [betterleaks/betterleaks](https://github.com/betterleaks/betterleaks) | MIT |
| [detect-secrets](detect-secrets.md) | [Yelp/detect-secrets](https://github.com/Yelp/detect-secrets) | Apache-2.0 |

### Static code analysis (SAST)

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [Semgrep](semgrep.md) (start here) | [semgrep/semgrep](https://github.com/semgrep/semgrep) | LGPL-2.1 |
| [Opengrep](opengrep.md) | [opengrep/opengrep](https://github.com/opengrep/opengrep) | LGPL-2.1 |
| [gosec](gosec.md) | [securego/gosec](https://github.com/securego/gosec) | Apache-2.0 |
| [Find Security Bugs](find-sec-bugs.md) | [find-sec-bugs/find-sec-bugs](https://github.com/find-sec-bugs/find-sec-bugs) | LGPL-3.0 |
| [eslint-plugin-security](eslint-security.md) | [eslint-community/eslint-plugin-security](https://github.com/eslint-community/eslint-plugin-security) | Apache-2.0 |
| [mobsfscan](mobsfscan.md) | [MobSF/mobsfscan](https://github.com/MobSF/mobsfscan) | LGPL-3.0 |
| [SonarQube](sonarqube.md) | [SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) | LGPL-3.0 (Community Build) |

### Dependency scanning (SCA)

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [osv-scanner](osv-scanner.md) (start here) | [google/osv-scanner](https://github.com/google/osv-scanner) | Apache-2.0 |
| [Trivy (filesystem)](trivy-fs.md) | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Apache-2.0 |
| [Grype](grype.md) | [anchore/grype](https://github.com/anchore/grype) | Apache-2.0 |
| [OWASP Dependency-Check](dependency-check.md) | [dependency-check/DependencyCheck](https://github.com/dependency-check/DependencyCheck) | Apache-2.0 |
| [retire.js](retire.md) | [RetireJS/retire.js](https://github.com/RetireJS/retire.js) | Apache-2.0 |

### Malware and malicious code

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [GuardDog](guarddog.md) (start here) | [DataDog/guarddog](https://github.com/DataDog/guarddog) | Apache-2.0 |
| [YARA-X](yara-x.md) | [VirusTotal/yara-x](https://github.com/VirusTotal/yara-x) | BSD-3-Clause |
| [ClamAV](clamav.md) | [Cisco-Talos/clamav](https://github.com/Cisco-Talos/clamav) | GPL-2.0 |
| [THOR Lite](thor-lite.md) | [Documentation](https://www.nextron-systems.com/thor-lite/) | Free for use, closed source (Nextron Systems) |
| [Claude Code security review](claude-security-review.md) | [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | MIT |

## 2. Secure the pipeline

### Pipeline security

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [poutine](poutine.md) (start here) | [boostsecurityio/poutine](https://github.com/boostsecurityio/poutine) | Apache-2.0 |
| [zizmor](zizmor.md) | [zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) | MIT |
| [actionlint](actionlint.md) | [rhysd/actionlint](https://github.com/rhysd/actionlint) | MIT |
| [pinact](pinact.md) | [suzuki-shunsuke/pinact](https://github.com/suzuki-shunsuke/pinact) | MIT |
| [Harden-Runner](harden-runner.md) | [step-security/harden-runner](https://github.com/step-security/harden-runner) | Apache-2.0 |
| [Checkov (gitlab_ci)](checkov-cicd.md) | [bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) | Apache-2.0 |
| [OpenSSF Scorecard](scorecard.md) | [ossf/scorecard](https://github.com/ossf/scorecard) | Apache-2.0 |

### Secrets management

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [HashiCorp Vault](vault.md) (start here) | [hashicorp/vault](https://github.com/hashicorp/vault) | BUSL-1.1 |
| [SOPS](sops.md) | [getsops/sops](https://github.com/getsops/sops) | MPL-2.0 |
| [External Secrets Operator](external-secrets.md) | [external-secrets/external-secrets](https://github.com/external-secrets/external-secrets) | Apache-2.0 |

## 3. Harden containers

### Container images

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [hadolint](hadolint.md) (start here) | [hadolint/hadolint](https://github.com/hadolint/hadolint) | GPL-3.0 |
| [Trivy (image)](trivy-image.md) | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Apache-2.0 |
| [Dockle](dockle.md) | [goodwithtech/dockle](https://github.com/goodwithtech/dockle) | Apache-2.0 |
| [distroless base images](distroless.md) | [GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless) | Apache-2.0 |
| [skopeo](skopeo.md) | [podman-container-tools/skopeo](https://github.com/podman-container-tools/skopeo) | Apache-2.0 |
| [crane](crane.md) | [google/go-containerregistry](https://github.com/google/go-containerregistry) | Apache-2.0 |

## 4. Check infrastructure code

### Infrastructure as code

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [Checkov](checkov.md) (start here) | [bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) | Apache-2.0 |
| [KICS](kics.md) | [Checkmarx/kics](https://github.com/Checkmarx/kics) | Apache-2.0 |
| [conftest](conftest.md) | [open-policy-agent/conftest](https://github.com/open-policy-agent/conftest) | Apache-2.0 |
| [Trivy (config)](trivy-config.md) | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Apache-2.0 |
| [terraform-compliance](terraform-compliance.md) | [terraform-compliance/cli](https://github.com/terraform-compliance/cli) | MIT |

## 5. Trust your artifacts

### SBOM, signing, and provenance

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [syft](syft.md) (start here) | [anchore/syft](https://github.com/anchore/syft) | Apache-2.0 |
| [cdxgen](cdxgen.md) | [cdxgen/cdxgen](https://github.com/cdxgen/cdxgen) | Apache-2.0 |
| [cosign](cosign.md) (start here) | [sigstore/cosign](https://github.com/sigstore/cosign) | Apache-2.0 |
| [SLSA GitHub generator](slsa-github-generator.md) | [slsa-framework/slsa-github-generator](https://github.com/slsa-framework/slsa-github-generator) | Apache-2.0 |
| [slsa-verifier](slsa-verifier.md) | [slsa-framework/slsa-verifier](https://github.com/slsa-framework/slsa-verifier) | Apache-2.0 |
| [witness](witness.md) | [in-toto/witness](https://github.com/in-toto/witness) | Apache-2.0 |
| [sbomqs](sbomqs.md) | [interlynk-io/sbomqs](https://github.com/interlynk-io/sbomqs) | Apache-2.0 |

## 6. Guard Kubernetes

### Kubernetes admission and audit

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [Kyverno](kyverno.md) (start here) | [kyverno/kyverno](https://github.com/kyverno/kyverno) | Apache-2.0 |
| [Chainsaw](chainsaw.md) | [kyverno/chainsaw](https://github.com/kyverno/chainsaw) | Apache-2.0 |
| [Gatekeeper](gatekeeper.md) | [open-policy-agent/gatekeeper](https://github.com/open-policy-agent/gatekeeper) | Apache-2.0 |
| [kube-linter](kube-linter.md) | [stackrox/kube-linter](https://github.com/stackrox/kube-linter) | Apache-2.0 |
| [Kubescape](kubescape.md) | [kubescape/kubescape](https://github.com/kubescape/kubescape) | Apache-2.0 |
| [kube-bench](kube-bench.md) | [aquasecurity/kube-bench](https://github.com/aquasecurity/kube-bench) | Apache-2.0 |

### Runtime detection

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [Falco](falco.md) (start here) | [falcosecurity/falco](https://github.com/falcosecurity/falco) | Apache-2.0 |

## 7. Test what runs

### Dynamic testing (DAST)

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [OWASP ZAP](zap.md) (start here) | [zaproxy/zaproxy](https://github.com/zaproxy/zaproxy) | Apache-2.0 |
| [nuclei](nuclei.md) | [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) | MIT |
| [Schemathesis](schemathesis.md) | [schemathesis/schemathesis](https://github.com/schemathesis/schemathesis) | MIT |
| [RESTler](restler.md) | [microsoft/restler-fuzzer](https://github.com/microsoft/restler-fuzzer) | MIT |
| [Dalfox](dalfox.md) | [hahwul/dalfox](https://github.com/hahwul/dalfox) | MIT |
| [Burp Suite](burp.md) | [Documentation](https://portswigger.net/burp/documentation) | Commercial; free Community Edition |

### Mobile app builds

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [MobSF](mobsf.md) (start here) | [MobSF/Mobile-Security-Framework-MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) | GPL-3.0 |
| [apkleaks](apkleaks.md) | [dwisiswant0/apkleaks](https://github.com/dwisiswant0/apkleaks) | Apache-2.0 |
| [jadx](jadx.md) | [skylot/jadx](https://github.com/skylot/jadx) | Apache-2.0 |
| [Apktool](apktool.md) | [iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool) | Apache-2.0 |

## 8. Secure the cloud

### Cloud posture (CSPM)

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [Prowler](prowler.md) (start here) | [prowler-cloud/prowler](https://github.com/prowler-cloud/prowler) | Apache-2.0 |
| [ScoutSuite](scoutsuite.md) | [nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) | GPL-2.0 |
| [Cloud Custodian](cloud-custodian.md) | [cloud-custodian/cloud-custodian](https://github.com/cloud-custodian/cloud-custodian) | Apache-2.0 |
| [Steampipe and Powerpipe](steampipe.md) | [turbot/steampipe](https://github.com/turbot/steampipe) | AGPL-3.0 |
| [CloudSploit](cloudsploit.md) | [aquasecurity/cloudsploit](https://github.com/aquasecurity/cloudsploit) | GPL-3.0 |

### Cloud identity and access

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [PMapper](pmapper.md) (start here) | [nccgroup/PMapper](https://github.com/nccgroup/PMapper) | AGPL-3.0 |
| [Cloudsplaining](cloudsplaining.md) | [salesforce/cloudsplaining](https://github.com/salesforce/cloudsplaining) | BSD-3-Clause |

### Native cloud security services

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [AWS Security Hub and GuardDuty](aws-security-hub.md) (start here) | [Documentation](https://docs.aws.amazon.com/securityhub/) | AWS service (paid) |
| [Google Security Command Center](gcp-scc.md) | [Documentation](https://cloud.google.com/security-command-center/docs) | Google Cloud service |
| [Microsoft Defender for Cloud](azure-defender.md) | [Documentation](https://learn.microsoft.com/azure/defender-for-cloud/) | Azure service |

### Cloud secrets and keys

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [AWS Secrets Manager](aws-secrets-manager.md) (start here) | [Documentation](https://docs.aws.amazon.com/secretsmanager/) | AWS service (paid) |
| [Azure Key Vault](azure-key-vault.md) | [Documentation](https://learn.microsoft.com/azure/key-vault/) | Azure service |
| [Google Secret Manager](gcp-secret-manager.md) | [Documentation](https://cloud.google.com/secret-manager/docs) | Google Cloud service |

## 9. Run the program

### Vulnerability management and release gates

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [DefectDojo](defectdojo.md) (start here) | [DefectDojo/django-DefectDojo](https://github.com/DefectDojo/django-DefectDojo) | BSD-3-Clause |
| [Dependency-Track](dependency-track.md) | [DependencyTrack/dependency-track](https://github.com/DependencyTrack/dependency-track) | Apache-2.0 |
| [secureCodeBox](securecodebox.md) | [secureCodeBox/secureCodeBox](https://github.com/secureCodeBox/secureCodeBox) | Apache-2.0 |

### Threat modeling

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [OWASP Threat Dragon](threat-dragon.md) (start here) | [OWASP/threat-dragon](https://github.com/OWASP/threat-dragon) | Apache-2.0 |
| [Threagile](threagile.md) | [Threagile/threagile](https://github.com/Threagile/threagile) | MIT |
| [pytm](pytm.md) | [OWASP/pytm](https://github.com/OWASP/pytm) | MIT |
| [threatcl](threatcl.md) | [threatcl/threatcl](https://github.com/threatcl/threatcl) | MIT |

### People, standards, and maturity

| Manual | Tool repository | License |
| :--- | :--- | :--- |
| [OWASP DSOMM](dsomm.md) (start here) | [devsecopsmaturitymodel/DevSecOps-MaturityModel](https://github.com/devsecopsmaturitymodel/DevSecOps-MaturityModel) | GPL-3.0 |
| [OWASP SAMM](samm.md) | [owaspsamm/core](https://github.com/owaspsamm/core) | CC-BY-SA-4.0 |
| [OWASP ASVS](asvs.md) | [OWASP/ASVS](https://github.com/OWASP/ASVS) | CC-BY-SA-4.0 |
| [OWASP MASVS](masvs.md) | [OWASP/masvs](https://github.com/OWASP/masvs) | CC-BY-SA-4.0 |
| [GoPhish](gophish.md) | [gophish/gophish](https://github.com/gophish/gophish) | MIT |

**Status:** 91 generated manuals. Commands come from each project's own documentation; test CI examples in your own pipeline before relying on them.
