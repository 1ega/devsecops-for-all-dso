/* Roadmap content. Commands were checked against each project's own README and docs.
   Pin every image tag and binary version before using a job in production. */
window.ROADMAP = {
  repoBase: 'https://github.com/1ega/devsecopsforall/tree/main/',
  manualBase: 'https://github.com/1ega/devsecopsforall/blob/main/manuals/',
  scopes: ['Code', 'Pipeline', 'Containers', 'Cloud', 'Kubernetes', 'Running apps', 'Team'],

  // The nine areas on the main screen, left to right. Each groups one or more stages.
  areas: [
    { id: 'code', title: 'Protect your code', short: 'Secrets, code, dependencies, malware', stages: ['secrets', 'sast', 'sca', 'malware'] },
    { id: 'pipeline', title: 'Secure the pipeline', short: 'Runners, variables, vaults', stages: ['cicd', 'vault'] },
    { id: 'containers', title: 'Harden containers', short: 'Dockerfiles and images', stages: ['containers'] },
    { id: 'iac', title: 'Check infrastructure code', short: 'Terraform, Helm, manifests', stages: ['iac'] },
    { id: 'artifacts', title: 'Trust your artifacts', short: 'SBOM, signing, provenance', stages: ['supply'] },
    { id: 'k8s', title: 'Guard Kubernetes', short: 'Admission, audit, runtime', stages: ['k8s', 'runtime'] },
    { id: 'test', title: 'Test what runs', short: 'Web, API, mobile builds', stages: ['dast', 'mobile'] },
    { id: 'cloud', title: 'Secure the cloud', short: 'Posture, IAM, native services, keys', stages: ['cloud', 'cloud-iam', 'cloud-native', 'cloud-secrets'] },
    { id: 'program', title: 'Run the program', short: 'Findings, threats, maturity', stages: ['vm', 'tm', 'maturity'] },
  ],

  phases: [
    { id: 'code', title: 'Protect the code', goal: 'Stop secrets, vulnerable code, and known-bad dependencies before they are merged. These checks are cheap to add and give results on day one.' },
    { id: 'build', title: 'Secure the pipeline and the build', goal: 'Treat the pipeline as production: lock down how jobs get credentials, what they build on, and what infrastructure they create.' },
    { id: 'ship', title: 'Ship artifacts you can trust', goal: 'Know what is inside every release, sign it, and refuse anything unsigned or non-compliant at the cluster door.' },
    { id: 'run', title: 'Test and watch what runs', goal: 'Attack the running application, check built mobile apps, and keep an eye on cloud accounts and containers after deploy.' },
    { id: 'program', title: 'Run it as a program', goal: 'Collect every finding in one place, decide what blocks a release, design security in early, and measure maturity over time.' },
  ],

  stages: [
    /* ------------------------------------------------------------------ PHASE 1 */
    {
      id: 'secrets', phase: 'code', title: 'Secret scanning',
      goal: 'Find API keys, tokens, and passwords in code and git history before an attacker does.',
      appliesTo: ['Code', 'Pipeline'],
      keywords: 'secrets credentials leaks keys tokens passwords',
      builtins: [
        { platform: 'GitHub', text: 'Secret scanning and push protection are free for public repositories; private repositories need GitHub Secret Protection.' },
        { platform: 'GitLab', text: '<code>include: - template: Jobs/Secret-Detection.gitlab-ci.yml</code> runs on every tier. The merge request widget, vulnerability report, and push protection need GitLab Ultimate.' },
      ],
      concepts: ['Secret detection', 'Pre-commit hooks', 'Full git history scans', 'Verified vs unverified findings', 'Rotate first, then remove', 'Secret zero'],
      tools: [
        {
          id: 'gitleaks', name: 'gitleaks', pick: 'start', repo: 'gitleaks/gitleaks', license: 'MIT',
          docs: 'https://github.com/gitleaks/gitleaks#readme', repoPath: 'scanners/gitleaks',
          role: 'Fast regex and entropy scanner for git history, directories, and stdin.',
          gitlab: 'SARIF and JSON reports',
          why: 'The most widely used open-source secret scanner, with a simple TOML config you can extend with your own rules (<code>[extend] useDefault = true</code>). Start with it in pre-commit and in pull request pipelines.',
          caution: 'The README says gitleaks is feature complete and will receive security patches only; its author now develops betterleaks. It remains a solid choice today.',
          install: [
            { label: 'macOS or Linux (Homebrew)', code: 'brew install gitleaks' },
            { label: 'Container image', code: 'docker pull zricethezav/gitleaks:latest\n# or ghcr.io/gitleaks/gitleaks:latest' },
          ],
          run: [
            { label: 'Scan the git history of the current repository', code: 'gitleaks git -v .' },
            { label: 'Scan a directory without git history', code: 'gitleaks dir -v path/to/project' },
            { label: 'Write a SARIF report', code: 'gitleaks git --report-format sarif --report-path gitleaks.sarif .' },
          ],
          ci: `secret-scan:
  stage: test
  image:
    name: zricethezav/gitleaks:latest   # pin a version tag
    entrypoint: [""]
  variables:
    GIT_DEPTH: 0                        # full history for the scan
  script:
    - gitleaks git --report-format sarif --report-path gitleaks.sarif .
  artifacts:
    when: always
    paths: [gitleaks.sarif]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`,
          results: 'Exit code 0 means no leaks; 1 means leaks were found (change it with <code>--exit-code</code>). Treat every finding as compromised: rotate the secret first, then remove it from history. Add justified false positives to <code>.gitleaksignore</code>. Import the SARIF file into DefectDojo as "Gitleaks Scan" or "SARIF".',
        },
        {
          id: 'trufflehog', name: 'TruffleHog', repo: 'trufflesecurity/trufflehog', license: 'AGPL-3.0',
          docs: 'https://docs.trufflesecurity.com',
          role: 'Finds secrets and checks with the provider whether they still work.',
          gitlab: 'Ready GitLab CI example upstream',
          why: 'Verification removes most noise: <code>--results=verified</code> shows only credentials that still authenticate. It can also scan a whole GitLab instance, issues and all, with <code>trufflehog gitlab</code>.',
          caution: 'Verification makes network calls to the providers of the secrets it finds. Check that this is acceptable before running it in CI.',
          install: [
            { label: 'Homebrew', code: 'brew install trufflehog' },
            { label: 'Install script', code: 'curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin' },
            { label: 'Container image', code: 'docker pull trufflesecurity/trufflehog:latest' },
          ],
          run: [
            { label: 'Scan the local repository, fail on live or unknown secrets', code: 'trufflehog git file://. --results=verified,unknown --fail' },
            { label: 'Scan a directory', code: 'trufflehog filesystem path/to/dir' },
            { label: 'JSON or SARIF output', code: 'trufflehog git file://. --json > trufflehog.jsonl\ntrufflehog filesystem . --sarif --no-verification > trufflehog.sarif' },
          ],
          ci: `trufflehog:
  stage: test
  image: alpine:3.20
  variables:
    SCAN_PATH: "."
  before_script:
    - apk add --no-cache git curl jq
    - curl -sSfL https://raw.githubusercontent.com/trufflesecurity/trufflehog/main/scripts/install.sh | sh -s -- -b /usr/local/bin
  script:
    - trufflehog filesystem "$SCAN_PATH" --results=verified,unknown --fail --json | jq
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"`,
          results: 'Exit code 183 means secrets were found (only with <code>--fail</code>), 1 means an error, 0 means clean. Verified results are live credentials: revoke them immediately.',
        },
        {
          id: 'betterleaks', name: 'betterleaks', repo: 'betterleaks/betterleaks', license: 'MIT',
          docs: 'https://github.com/betterleaks/betterleaks#readme',
          role: 'Successor to gitleaks by the same author; reads .gitleaks.toml and validates findings.',
          gitlab: 'JSON reports; can scan GitLab issues, MRs, and CI logs',
          why: 'Worth watching if you already use gitleaks: it keeps the config format, adds rule validation, and can scan GitLab projects directly, including merge requests and CI job logs.',
          caution: 'Version 2 removed SARIF output: reports are JSON or JSONL only. Several flags were renamed from gitleaks, for example <code>--report-path</code> became <code>--output</code>.',
          install: [
            { label: 'Homebrew', code: 'brew install betterleaks' },
            { label: 'Go', code: 'go install github.com/betterleaks/betterleaks/v2@latest' },
            { label: 'Container image', code: 'docker pull ghcr.io/betterleaks/betterleaks:v2' },
          ],
          run: [
            { label: 'Scan the git history', code: 'betterleaks git .' },
            { label: 'Scan a directory to JSON', code: 'betterleaks fs . --output findings.json' },
            { label: 'Scan a GitLab project (reads GITLAB_TOKEN)', code: 'betterleaks gitlab https://gitlab.com/mygroup/myproject --include issues,mrs,releases,ci-jobs' },
          ],
          ci: `betterleaks:
  stage: test
  image:
    name: ghcr.io/betterleaks/betterleaks:v2
    entrypoint: [""]
  variables:
    GIT_DEPTH: 0
  script:
    - betterleaks git . --output betterleaks.json
  artifacts:
    when: always
    paths: [betterleaks.json]`,
          results: 'Exit code 1 when findings exist (change with <code>--exit-code</code>).',
        },
        {
          id: 'detect-secrets', name: 'detect-secrets', repo: 'Yelp/detect-secrets', license: 'Apache-2.0',
          docs: 'https://github.com/Yelp/detect-secrets#readme',
          role: 'Baseline workflow: record known findings once, then block only new secrets.',
          why: 'Fits large legacy repositories where a first scan finds hundreds of old findings. You audit the baseline once and the hook only fails on secrets that are not in it.',
          install: [{ label: 'pip or Homebrew', code: 'pip install detect-secrets\n# or\nbrew install detect-secrets' }],
          run: [
            { label: 'Create and review a baseline', code: 'detect-secrets scan > .secrets.baseline\ndetect-secrets audit .secrets.baseline' },
            { label: 'Fail on secrets that are not in the baseline', code: 'git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline' },
          ],
          ci: `detect-secrets:
  stage: test
  image: python:3.12-slim
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends git
    - pip install detect-secrets
  script:
    - git ls-files -z | xargs -0 detect-secrets-hook --baseline .secrets.baseline`,
          results: 'The hook exits 1 when it finds secrets missing from the baseline and 3 when it updated the baseline file. Commit the reviewed baseline to the repository.',
        },
      ],
    },
    {
      id: 'sast', phase: 'code', title: 'Static code analysis (SAST)',
      goal: 'Catch injection, unsafe APIs, and weak crypto in source code during review.',
      appliesTo: ['Code'],
      keywords: 'sast static analysis code review semgrep injection',
      builtins: [
        { platform: 'GitHub', text: 'Code scanning with CodeQL is free for public repositories; private repositories need GitHub Code Security. Code scanning also accepts SARIF from the tools below.' },
        { platform: 'GitLab', text: '<code>include: - template: Jobs/SAST.gitlab-ci.yml</code> runs analyzers for most languages on every tier. Merge request findings need GitLab Ultimate.' },
      ],
      concepts: ['Taint analysis', 'Injection: SQL, command, template', 'SSRF', 'Weak cryptography', 'False positives and triage', 'Diff-aware scans'],
      tools: [
        {
          id: 'semgrep', name: 'Semgrep', pick: 'start', repo: 'semgrep/semgrep', license: 'LGPL-2.1',
          docs: 'https://semgrep.dev/docs', repoPath: 'rules/semgrep',
          role: 'Pattern and taint rules for 30+ languages, with native GitLab SAST output.',
          gitlab: 'Writes GitLab SAST reports',
          why: 'Rules look like the code they match, so the team can write its own. This repository ships rule packs for mobile, Python, and backend languages; GitLab reads the <code>--gitlab-sast-output</code> file natively.',
          install: [
            { label: 'pip or Homebrew', code: 'python3 -m pip install semgrep\n# or\nbrew install semgrep' },
            { label: 'Container image', code: 'docker pull semgrep/semgrep' },
          ],
          run: [
            { label: 'Scan with a local rule pack', code: 'semgrep scan --metrics=off --config rules/semgrep/trailofbits/ path/to/project' },
            { label: 'Write SARIF, JSON, and GitLab reports in one run', code: 'semgrep scan --metrics=off --config rules/semgrep/ \\\n  --sarif-output=semgrep.sarif --json-output=semgrep.json \\\n  --gitlab-sast-output=gl-sast-report.json .' },
          ],
          ci: `semgrep:
  stage: test
  image: semgrep/semgrep            # no entrypoint override needed
  variables:
    SEMGREP_RULES: rules/semgrep/  # path to the Semgrep rule pack
  script:
    - semgrep scan --metrics=off --config "$SEMGREP_RULES"
        --gitlab-sast-output=gl-sast-report.json
        --sarif-output=semgrep.sarif .
  artifacts:
    when: always
    paths: [semgrep.sarif]
    reports:
      sast: gl-sast-report.json
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`,
          results: 'Add <code>--error</code> to exit 1 when there are findings, which fails the job. Registry configs such as <code>p/ci</code> send pseudonymous metrics; local rule paths with <code>--metrics=off</code> do not. Import JSON into DefectDojo as "Semgrep JSON Report".',
        },
        {
          id: 'opengrep', name: 'Opengrep', repo: 'opengrep/opengrep', license: 'LGPL-2.1',
          docs: 'https://github.com/opengrep/opengrep/wiki',
          role: 'Community fork of the Semgrep engine with the same rule format and CLI.',
          gitlab: 'Writes GitLab SAST reports',
          why: 'Choose it if you want an engine whose features are all open source. Existing Semgrep rules, including the packs in this repository, run unchanged.',
          install: [{ label: 'Install script (Linux and macOS)', code: 'curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash' }],
          run: [{ label: 'Scan with SARIF output', code: 'opengrep scan --sarif-output=opengrep.sarif -f rules/semgrep/ path/to/code' }],
          ci: `opengrep:
  stage: test
  image: debian:bookworm-slim
  before_script:
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
    - curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
    - export PATH="$HOME/.opengrep/cli/latest:$PATH"
  script:
    - opengrep scan -f rules/semgrep/ --gitlab-sast-output=gl-sast-report.json .
  artifacts:
    reports:
      sast: gl-sast-report.json`,
          results: '<code>--error</code> exits 1 on findings. No official container image is published; install with the script.',
        },
        {
          id: 'gosec', name: 'gosec', repo: 'securego/gosec', license: 'Apache-2.0',
          docs: 'https://securego.io/',
          role: 'Security checks for Go code: injection, weak crypto, unsafe file and network use.',
          why: 'Specialized for Go and aware of Go idioms, so it finds things generic rules miss. Run it next to Semgrep on Go services.',
          install: [
            { label: 'Go (needs Go 1.25+)', code: 'go install github.com/securego/gosec/v2/cmd/gosec@latest' },
            { label: 'Container image', code: 'docker pull ghcr.io/securego/gosec:latest' },
          ],
          run: [
            { label: 'Scan all packages', code: 'gosec ./...' },
            { label: 'SARIF output', code: 'gosec -fmt sarif -out gosec.sarif ./...' },
          ],
          ci: `gosec:
  stage: test
  image:
    name: ghcr.io/securego/gosec:latest
    entrypoint: [""]
  script:
    - gosec -fmt sarif -out gosec.sarif ./...
  artifacts:
    when: always
    paths: [gosec.sarif]`,
          results: 'Exit code 1 on any unsuppressed finding; <code>-no-fail</code> always returns 0. Suppress a reviewed line with <code>#nosec G104 -- reason</code>.',
        },
        {
          id: 'find-sec-bugs', name: 'Find Security Bugs', repo: 'find-sec-bugs/find-sec-bugs', license: 'LGPL-3.0',
          docs: 'https://find-sec-bugs.github.io/',
          role: 'SpotBugs plugin with security detectors for Java, Kotlin, and JVM frameworks.',
          why: 'Works on compiled bytecode, so it understands Spring, JAX-RS, and other frameworks deeply. Add it to the Maven or Gradle build you already have.',
          install: [
            { label: 'Maven: add the plugin to spotbugs-maven-plugin', code: '<plugin>\n  <groupId>com.github.spotbugs</groupId>\n  <artifactId>spotbugs-maven-plugin</artifactId>\n  <configuration>\n    <plugins>\n      <plugin>\n        <groupId>com.h3xstream.findsecbugs</groupId>\n        <artifactId>findsecbugs-plugin</artifactId>\n        <version>1.14.0</version>\n      </plugin>\n    </plugins>\n  </configuration>\n</plugin>' },
          ],
          run: [{ label: 'Run with Maven', code: 'mvn compile spotbugs:check' }],
          ci: `find-sec-bugs:
  stage: test
  image: maven:3-eclipse-temurin-21
  script:
    - mvn -B compile spotbugs:check
  artifacts:
    when: always
    paths: [target/spotbugsXml.xml]`,
          results: 'Results are SpotBugs XML in <code>target/</code>. For Gradle setup and the full configuration, follow the project wiki linked from the documentation page.',
        },
        {
          id: 'eslint-security', name: 'eslint-plugin-security', repo: 'eslint-community/eslint-plugin-security', license: 'Apache-2.0',
          docs: 'https://github.com/eslint-community/eslint-plugin-security#readme',
          role: 'ESLint rules for risky JavaScript and TypeScript patterns.',
          why: 'Runs inside the linter developers already use, so findings appear in the editor. Expect noise: the rules warn on patterns that need a human look.',
          install: [{ label: 'npm', code: 'npm install --save-dev eslint-plugin-security' }],
          run: [{ label: 'eslint.config.js (flat config)', code: "const pluginSecurity = require('eslint-plugin-security');\n\nmodule.exports = [pluginSecurity.configs.recommended];", lang: 'js' }],
          ci: `eslint-security:
  stage: test
  image: node:22
  script:
    - npm ci
    - npx eslint . --max-warnings 0`,
          results: 'All recommended rules are warnings, so CI only fails with <code>--max-warnings 0</code> or when you raise rules to errors.',
        },
        {
          id: 'mobsfscan', name: 'mobsfscan', repo: 'MobSF/mobsfscan', license: 'LGPL-3.0',
          docs: 'https://github.com/MobSF/mobsfscan#readme', repoPath: 'rules/semgrep/mobile',
          role: 'Source code checks for Android and iOS apps with native GitLab SAST output.',
          gitlab: 'Writes GitLab SAST reports',
          why: 'The quickest way to add mobile-specific checks to a GitLab pipeline. Combine it with the mobile Semgrep pack in this repository for deeper coverage.',
          install: [{ label: 'pip or container image', code: 'pip install mobsfscan\n# or\ndocker pull opensecurity/mobsfscan' }],
          run: [{ label: 'Scan with SARIF output', code: 'mobsfscan . --sarif --output mobsfscan.sarif' }],
          ci: `mobsfscan:
  stage: test
  image: python:3.12
  before_script:
    - pip3 install --upgrade mobsfscan
  script:
    - mobsfscan . --gitlab-sast -o gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json`,
          results: 'Exit code 1 on ERROR-severity findings; <code>--exit-warning</code> also fails on warnings and <code>--no-fail</code> always returns 0.',
        },
        {
          id: 'sonarqube', name: 'SonarQube', repo: 'SonarSource/sonarqube', license: 'LGPL-3.0 (Community Build)',
          docs: 'https://docs.sonarsource.com/sonarqube-community-build/',
          role: 'Code quality and security server with quality gates and per-branch dashboards.',
          why: 'Many teams already run it for code quality; its security rules and quality gates give developers one dashboard. Branch and pull request analysis need a commercial edition.',
          install: [{ label: 'Run the server (Community Build)', code: 'docker run -d --name sonarqube -p 9000:9000 sonarqube:community' }],
          run: [{ label: 'Analyze a project with the scanner CLI', code: 'docker run --rm -v "$PWD:/usr/src" \\\n  -e SONAR_HOST_URL="http://sonarqube.example.com" -e SONAR_TOKEN="$SONAR_TOKEN" \\\n  sonarsource/sonar-scanner-cli -Dsonar.projectKey=my-app' }],
          results: 'Configure the project in <code>sonar-project.properties</code>. Findings can be exported to DefectDojo with its SonarQube parser.',
        },
      ],
    },
    {
      id: 'sca', phase: 'code', title: 'Dependency scanning (SCA)',
      goal: 'Find known vulnerabilities and risky packages in the libraries you depend on.',
      appliesTo: ['Code', 'Containers'],
      keywords: 'sca dependencies libraries cve lockfile packages',
      builtins: [
        { platform: 'GitHub', text: 'Dependabot alerts and security updates work on every plan. The dependency review action blocks pull requests that add vulnerable packages (private repositories need GitHub Code Security).' },
        { platform: 'GitLab', text: '<code>include: - template: Jobs/Dependency-Scanning.gitlab-ci.yml</code> requires GitLab Ultimate. The tools below work on any tier.' },
      ],
      concepts: ['CVE, CPE, and NVD', 'Known exploited vulnerabilities (KEV)', 'Reachability analysis', 'Lockfiles', 'Dependency confusion', 'Typosquatting', 'End-of-life software'],
      tools: [
        {
          id: 'osv-scanner', name: 'osv-scanner', pick: 'start', repo: 'google/osv-scanner', license: 'Apache-2.0',
          docs: 'https://google.github.io/osv-scanner', repoPath: 'scanners/osv-scanner',
          role: "Matches lockfiles against Google's OSV database, with offline mode.",
          why: 'Free, fast, and precise: OSV data maps vulnerabilities to exact package versions, which keeps false positives low. Reads Gradle, npm, pip, Go, Cargo, and pub lockfiles.',
          install: [
            { label: 'Homebrew or Go', code: 'brew install osv-scanner\n# or\ngo install github.com/google/osv-scanner/v2/cmd/osv-scanner@latest' },
            { label: 'Container image', code: 'docker pull ghcr.io/google/osv-scanner:latest' },
          ],
          run: [
            { label: 'Scan a project recursively', code: 'osv-scanner scan source -r .' },
            { label: 'SARIF output', code: 'osv-scanner scan source -r --format sarif --output-file osv.sarif .' },
          ],
          ci: `osv-scanner:
  stage: test
  image:
    name: ghcr.io/google/osv-scanner:latest
    entrypoint: [""]
  script:
    - /osv-scanner scan source -r --format sarif --output-file osv.sarif .
  artifacts:
    when: always
    paths: [osv.sarif]
  allow_failure:
    exit_codes: [128]          # no lockfiles found`,
          results: 'Exit code 1 when vulnerabilities are found, 128 when no packages were found (common in repositories without lockfiles). Check CocoaPods and Swift Package Manager support in the docs before relying on it for iOS.',
        },
        {
          id: 'trivy-fs', name: 'Trivy (filesystem)', repo: 'aquasecurity/trivy', license: 'Apache-2.0',
          docs: 'https://trivy.dev/docs/latest/', repoPath: 'scanners/trivy',
          role: 'One scanner for dependencies, secrets, and misconfiguration in a source tree.',
          gitlab: 'GitLab report templates included',
          why: 'Reads mobile lockfiles too (Gradle, pubspec.lock, Podfile.lock, Package.resolved) and ships templates that produce GitLab reports. One tool can cover dependencies, containers, and IaC.',
          caution: 'In March 2026 trivy-action, setup-trivy, and Trivy images on Docker Hub were reported compromised. Pin the image by digest and verify its signature.',
          install: [
            { label: 'Homebrew', code: 'brew install trivy' },
            { label: 'Install script', code: 'curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sudo sh -s -- -b /usr/local/bin' },
          ],
          run: [
            { label: 'Scan dependencies, secrets, and misconfiguration', code: 'trivy fs --scanners vuln,secret,misconfig .' },
            { label: 'SARIF output', code: 'trivy fs --format sarif -o trivy.sarif .' },
          ],
          ci: `trivy-fs:
  stage: test
  image:
    name: aquasec/trivy:latest        # pin by digest
    entrypoint: [""]
  variables:
    TRIVY_NO_PROGRESS: "true"
    TRIVY_CACHE_DIR: .trivycache/
  script:
    - trivy fs --scanners misconfig,vuln --exit-code 0
        --format template --template "@/contrib/gitlab-codequality.tpl"
        -o gl-codeclimate-fs.json .
  cache:
    paths: [.trivycache/]
  artifacts:
    reports:
      codequality: gl-codeclimate-fs.json`,
          results: 'Trivy exits 0 even when it finds issues; add <code>--exit-code 1 --severity CRITICAL</code> to gate. Import JSON into DefectDojo as "Trivy Scan".',
        },
        {
          id: 'grype', name: 'Grype', repo: 'anchore/grype', license: 'Apache-2.0',
          docs: 'https://oss.anchore.com/docs/', repoPath: 'scanners/grype',
          role: 'Vulnerability matcher for directories, images, and SBOMs.',
          why: 'Pairs with syft: generate the SBOM once, then scan it with Grype at every stage without rebuilding.',
          install: [{ label: 'Install script', code: 'curl -sSfL https://get.anchore.io/grype | sudo sh -s -- -b /usr/local/bin' }],
          run: [
            { label: 'Scan a directory or an SBOM', code: 'grype ./my-project\ngrype sbom:./sbom.json' },
            { label: 'SARIF output, fail on high', code: 'grype dir:. -o sarif --file grype.sarif --fail-on high' },
          ],
          ci: `grype:
  stage: test
  image: alpine:3.20                # the official image has no shell
  before_script:
    - apk add --no-cache curl
    - curl -sSfL https://get.anchore.io/grype | sh -s -- -b /usr/local/bin
  script:
    - grype dir:. -o sarif --file grype.sarif --fail-on high
  artifacts:
    when: always
    paths: [grype.sarif]`,
          results: '<code>--fail-on</code> returns exit code 2 when a match is at or above the given severity.',
        },
        {
          id: 'dependency-check', name: 'OWASP Dependency-Check', repo: 'dependency-check/DependencyCheck', license: 'Apache-2.0',
          docs: 'https://dependency-check.github.io/DependencyCheck',
          role: 'NVD-based scanner, strongest for Java and .NET, with a GitLab report format.',
          gitlab: 'Writes GitLab dependency scanning reports',
          why: 'Mature and audit-friendly, with a native GitLab format. It needs an NVD API key and a cached data directory, otherwise updates are very slow.',
          install: [
            { label: 'Homebrew', code: 'brew install dependency-check' },
            { label: 'Container image', code: 'docker pull owasp/dependency-check' },
          ],
          run: [{ label: 'Scan and write all report formats', code: 'dependency-check.sh --project "my-app" --scan . --format ALL --out reports/ --nvdApiKey "$NVD_API_KEY"' }],
          ci: `dependency-check:
  stage: test
  image:
    name: owasp/dependency-check:latest
    entrypoint: [""]
  script:
    - /usr/share/dependency-check/bin/dependency-check.sh
        --project "$CI_PROJECT_NAME" --scan .
        --format GITLAB --format SARIF --out reports/
        --nvdApiKey "$NVD_API_KEY" --failOnCVSS 9
  cache:
    paths: [/usr/share/dependency-check/data]   # mount or cache the NVD data
  artifacts:
    when: always
    paths: [reports/]
    reports:
      dependency_scanning: reports/dependency-check-gitlab.json`,
          results: 'By default it never fails; <code>--failOnCVSS 9</code> exits 15 when a CVSS score of 9 or higher is found. Request a free NVD API key and store it as a masked CI/CD variable.',
        },
        {
          id: 'retire', name: 'retire.js', repo: 'RetireJS/retire.js', license: 'Apache-2.0',
          docs: 'https://github.com/RetireJS/retire.js#readme',
          role: 'Finds JavaScript libraries with known vulnerabilities, including copies vendored into static files.',
          why: 'Catches jQuery, Angular, and other libraries copied into <code>static/</code> folders, which lockfile scanners never see.',
          install: [{ label: 'npm', code: 'npm install -g retire' }],
          run: [
            { label: 'Scan the current project', code: 'retire' },
            { label: 'CycloneDX SBOM output', code: 'retire --outputformat cyclonedx' },
          ],
          results: 'Exits with code 13 when it finds vulnerabilities; override with <code>--exitwith 0</code>.',
        },
      ],
    },

    /* ------------------------------------------------------------------ PHASE 2 */
    {
      id: 'malware', phase: 'code', title: 'Malware and malicious code',
      goal: 'Catch deliberately malicious code: backdoors in your repositories, malicious packages, and malware inside images and artifacts.',
      appliesTo: ['Code', 'Containers'],
      keywords: 'malware malicious backdoor packages typosquatting yara ioc antivirus supply chain attack',
      concepts: ['Malicious packages', 'Typosquatting and dependency confusion', 'Backdoors and logic bombs', 'Obfuscated code', 'Indicators of compromise (IOC)', 'YARA rules'],
      tools: [
        {
          id: 'guarddog', name: 'GuardDog', pick: 'start', repo: 'DataDog/guarddog', license: 'Apache-2.0',
          docs: 'https://github.com/DataDog/guarddog#readme',
          role: 'Detects malicious PyPI, npm, Go, and GitHub Actions packages with source and metadata heuristics.',
          why: 'Looks for what vulnerability scanners ignore: install-time code execution, exfiltration, obfuscation, and typosquatted names. Check a package before you add it.',
          install: [{ label: 'pip, uvx, or container', code: 'pip install guarddog\n# or\nuvx guarddog --help\n# or\ndocker run --rm ghcr.io/datadog/guarddog --help' }],
          run: [
            { label: 'Scan a package before adding it', code: 'guarddog pypi scan requests\nguarddog npm scan express' },
            { label: 'Check every dependency in a requirements file', code: 'guarddog pypi verify requirements.txt' },
          ],
          results: 'Each finding names the rule that matched, for example <code>exec-base64</code> or <code>code-execution</code>. Narrow or exclude rules with <code>--rules</code> and <code>--exclude-rules</code>.',
        },
        {
          id: 'yara-x', name: 'YARA-X', repo: 'VirusTotal/yara-x', license: 'BSD-3-Clause',
          docs: 'https://virustotal.github.io/yara-x/', repoPath: 'skills/trailofbits/yara-authoring',
          role: 'Pattern-matching rules for malware and suspicious files; the Rust successor to YARA.',
          why: 'The standard language for describing malware. Run community or your own rules over repositories, build output, and image filesystems. Classic YARA (VirusTotal/yara) uses the same rules.',
          install: [{ label: 'Homebrew or Cargo', code: 'brew install yara-x\n# or\ncargo install yara-x-cli' }],
          run: [{ label: 'Scan a directory with a rule file', code: 'yr scan rules/malware.yar path/to/scan' }],
          results: 'Start with curated community rule sets and tune them; broad rules produce many false positives on source code.',
        },
        {
          id: 'clamav', name: 'ClamAV', repo: 'Cisco-Talos/clamav', license: 'GPL-2.0',
          docs: 'https://docs.clamav.net/',
          role: 'Open-source antivirus engine for files, archives, and uploads.',
          why: 'A simple last check on build artifacts, image filesystems, and user uploads, with signature updates from Cisco Talos.',
          install: [{ label: 'Homebrew or container', code: 'brew install clamav\n# or\ndocker pull clamav/clamav' }],
          run: [{ label: 'Update signatures, then scan recursively and list only infected files', code: 'freshclam\nclamscan -r -i path/to/scan' }],
          results: '<code>clamscan</code> exits 1 when it finds infected files. Signature-based detection misses targeted, custom malware; combine it with YARA and code review.',
        },
        {
          id: 'thor-lite', name: 'THOR Lite', license: 'Free for use, closed source (Nextron Systems)',
          docs: 'https://www.nextron-systems.com/thor-lite/',
          role: 'IOC and YARA-based compromise assessment scanner, free edition.',
          why: 'Ships thousands of curated YARA rules and IOCs from a threat-intelligence vendor. Useful for scanning unpacked image filesystems and hosts for known malware and hacktools.',
          caution: 'Download requires registration, and the license file must be renewed periodically. It is not open source.',
          install: [{ label: 'Download from Nextron after registering', code: '# https://www.nextron-systems.com/thor-lite/\n./thor-lite-linux-64 --help' }],
        },
        {
          id: 'claude-security-review', name: 'Claude Code security review', repo: 'anthropics/claude-code-security-review', license: 'MIT',
          docs: 'https://github.com/anthropics/claude-code-security-review#readme', repoPath: 'skills',
          role: 'AI review of code changes for vulnerabilities and suspicious logic, as a GitHub Action or the /security-review command.',
          why: 'An AI reviewer reads intent, so it can flag hidden callbacks, credential harvesting, or time bombs that pattern rules miss. Pair it with Semgrep, as a malicious-code scan built on Claude Code does.',
          caution: 'Results depend on the model and can include false positives or misses; keep a human in the loop for anything it marks as malicious.',
          run: [{ label: 'In Claude Code, review pending changes', code: '/security-review' }],
          github: `name: Security review
on: [pull_request]
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
        with:
          fetch-depth: 2
      - uses: anthropics/claude-code-security-review@main   # pin to a commit SHA
        with:
          comment-pr: true
          claude-api-key: \${{ secrets.CLAUDE_API_KEY }}`,
          results: 'Comments land on the pull request. The API key must be enabled for both the Claude API and Claude Code.',
        },
      ],
    },
    {
      id: 'cicd', phase: 'build', title: 'Pipeline security',
      goal: 'Make sure the pipeline itself cannot be abused to steal secrets or push malicious builds.',
      appliesTo: ['Pipeline'],
      keywords: 'cicd pipeline gitlab-ci runners variables poisoned pipeline',
      builtins: [
        { platform: 'GitHub', text: 'Make the default GITHUB_TOKEN read-only, pin actions by commit SHA, require approval for workflows from forks, and use OIDC (<code>permissions: id-token: write</code>) instead of long-lived cloud keys.' },
        { platform: 'GitLab', text: 'Use protected branches and tags, protected and masked CI/CD variables, separate runners for protected branches, and <code>id_tokens</code> (OIDC) instead of long-lived cloud keys. Pipeline execution policies (Ultimate) can force security jobs into every project.' },
      ],
      concepts: ['Hosted vs self-hosted runners', 'Protected and masked variables', 'Pipeline templates and includes', 'Pipeline triggers', 'Poisoned pipeline execution', 'OIDC id_tokens', 'Unpinned images and includes'],
      tools: [
        {
          id: 'poutine', name: 'poutine', pick: 'start', repo: 'boostsecurityio/poutine', license: 'Apache-2.0',
          docs: 'https://boostsecurityio.github.io/poutine/', repoPath: 'policies/cicd/poutine-rego',
          role: 'Finds injection, unpinned includes, and risky runners in .gitlab-ci.yml and other pipelines.',
          gitlab: 'Understands GitLab CI; scans groups via the API',
          why: 'One of the few pipeline scanners that understands GitLab CI as well as GitHub Actions. Its Rego rules are imported in this repository, so you can read exactly what each check looks for.',
          install: [
            { label: 'Homebrew', code: 'brew install poutine' },
            { label: 'Go', code: 'go install github.com/boostsecurityio/poutine@latest' },
          ],
          run: [
            { label: 'Scan the pipeline files in the current repository', code: 'poutine analyze_local .' },
            { label: 'Scan a whole GitLab group', code: 'poutine analyze_org my-group --scm gitlab \\\n  --scm-base-url https://gitlab.example.com --token "$GL_TOKEN"' },
          ],
          ci: `poutine:
  stage: test
  image: golang:1.27
  before_script:
    - go install github.com/boostsecurityio/poutine@latest
  script:
    - poutine analyze_local . --format sarif > poutine.sarif
    - poutine analyze_local . --fail-on-violation
  artifacts:
    when: always
    paths: [poutine.sarif]`,
          results: '<code>--fail-on-violation</code> exits 10 when violations are found. For GitLab API scans pass the token with <code>--token</code>; the CLI only reads <code>GH_TOKEN</code> from the environment. Disable the daily version check with <code>--disable-version-check</code>.',
        },
        {
          id: 'zizmor', name: 'zizmor', repo: 'zizmorcore/zizmor', license: 'MIT',
          docs: 'https://docs.zizmor.sh/',
          role: 'Static analysis for GitHub Actions: template injection, unpinned actions, excessive permissions.',
          gitlab: 'GitHub Actions only; SARIF output',
          why: 'The most thorough auditor for GitHub workflows. It finds the injection and token-permission mistakes behind most real Actions compromises.',
          install: [{ label: 'Homebrew, pipx, or container', code: 'brew install zizmor\n# or\npipx install zizmor\n# or\ndocker pull ghcr.io/zizmorcore/zizmor:latest' }],
          run: [
            { label: 'Audit the workflows in a repository', code: 'zizmor .' },
            { label: 'SARIF output', code: 'zizmor --format=sarif . > zizmor.sarif' },
          ],
          github: `name: zizmor
on:
  push:
    branches: [main]
  pull_request:
permissions: {}
jobs:
  zizmor:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
      actions: read
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
        with:
          persist-credentials: false
      - uses: zizmorcore/zizmor-action@v0.6.4`,
          results: 'Exit codes 11 to 14 give the highest finding severity (informational to high); with <code>--format=sarif</code> it exits 0 and the results live in the SARIF file.',
        },
        {
          id: 'actionlint', name: 'actionlint', repo: 'rhysd/actionlint', license: 'MIT',
          docs: 'https://github.com/rhysd/actionlint/tree/main/docs',
          role: 'Linter for GitHub Actions workflows, including shellcheck on run: steps.',
          gitlab: 'GitHub Actions only',
          why: 'Catches broken expressions, wrong types, and unsafe shell before a workflow ever runs. Cheap to add next to zizmor.',
          install: [{ label: 'Homebrew or Go', code: 'brew install actionlint\n# or\ngo install github.com/rhysd/actionlint/cmd/actionlint@latest' }],
          run: [{ label: 'Lint all workflows in the repository', code: 'actionlint' }],
          github: `name: actionlint
on: [pull_request]
permissions:
  contents: read
jobs:
  actionlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
      - name: Download actionlint
        run: bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
      - name: Lint workflows
        run: ./actionlint -color`,
          results: 'Exits non-zero when it finds errors. Output can be shaped with <code>-format</code>, including SARIF through a template.',
        },
        {
          id: 'pinact', name: 'pinact', repo: 'suzuki-shunsuke/pinact', license: 'MIT',
          docs: 'https://github.com/suzuki-shunsuke/pinact/tree/main/docs',
          role: 'Pins GitHub Actions and reusable workflows to full commit SHAs.',
          gitlab: 'GitHub Actions only',
          why: 'A moved tag is how many Actions supply-chain attacks spread. pinact rewrites <code>uses:</code> lines to SHAs with a version comment.',
          install: [{ label: 'Homebrew', code: 'brew install pinact' }],
          run: [
            { label: 'Pin every action in the repository', code: 'pinact run' },
            { label: 'Check only, for CI', code: 'pinact run --check' },
          ],
          results: 'Exit code 1 means something still needs pinning, 2 means an action cannot be fixed automatically, 3 means an API or usage error.',
        },
        {
          id: 'harden-runner', name: 'Harden-Runner', repo: 'step-security/harden-runner', license: 'Apache-2.0',
          docs: 'https://docs.stepsecurity.io/harden-runner',
          role: 'Monitors and blocks network egress and file changes on GitHub-hosted runners.',
          gitlab: 'GitHub Actions only',
          why: 'If a dependency or action is compromised, egress control stops it from sending your secrets out. Start in audit mode to learn what each job contacts.',
          caution: 'The free Community tier covers public repositories on GitHub-hosted runners; private repositories and self-hosted runners need the Enterprise tier.',
          run: [{ label: 'Add as the first step of every job', code: `steps:
  - name: Harden Runner
    uses: step-security/harden-runner@v2.21.1   # pin to a commit SHA
    with:
      egress-policy: audit`, lang: 'yaml' }],
          results: 'Each run links to a report of network and file events. Switch <code>egress-policy</code> to <code>block</code> with an allowlist once the audit is clean.',
        },
        {
          id: 'checkov-cicd', name: 'Checkov (gitlab_ci)', repo: 'bridgecrewio/checkov', license: 'Apache-2.0',
          docs: 'https://www.checkov.io/1.Welcome/Quick%20Start.html',
          role: 'Policy checks for .gitlab-ci.yml and GitLab project settings.',
          gitlab: 'gitlab_ci and gitlab_configuration frameworks; GitLab SAST output',
          why: 'If you already run Checkov for Terraform, the same tool checks pipeline files and GitLab configuration with no extra setup.',
          install: [{ label: 'pip or Homebrew', code: 'pip3 install checkov\n# or\nbrew install checkov' }],
          run: [{ label: 'Check pipeline definitions', code: 'checkov -d . --framework gitlab_ci' }],
          ci: `checkov-pipeline:
  stage: test
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d . --framework gitlab_ci -o cli -o gitlab_sast --output-file-path console,gl-sast-checkov.json
  artifacts:
    reports:
      sast: gl-sast-checkov.json`,
          results: 'Exits non-zero on failed checks; <code>--soft-fail</code> always returns 0, and <code>--hard-fail-on</code> limits failures to chosen check IDs or severities.',
        },
        {
          id: 'scorecard', name: 'OpenSSF Scorecard', repo: 'ossf/scorecard', license: 'Apache-2.0',
          docs: 'https://scorecard.dev',
          role: 'Scores a repository on security practices: reviews, pinning, branch protection.',
          gitlab: 'GitLab support, some checks still in validation',
          why: 'A quick health check of your own projects and of the open-source projects you depend on.',
          caution: 'On GitLab the Dangerous-Workflow, SAST, and Token-Permissions checks are unsupported, and several others are still being validated.',
          install: [{ label: 'Homebrew', code: 'brew install scorecard' }],
          run: [{ label: 'Score a GitLab project (token scopes: read_api, read_user, read_repository)', code: 'export GITLAB_AUTH_TOKEN=glpat-xxxx\nscorecard --repo gitlab.com/<group>/<project> --show-details' }],
          results: 'Each check scores 0 to 10 with a reason. Use <code>--format=json</code> for automation; SARIF exists in the code but needs <code>ENABLE_SARIF</code> set.',
        },
      ],
    },
    {
      id: 'vault', phase: 'build', title: 'Secrets management',
      goal: 'Give jobs and services short-lived credentials from a vault instead of storing secrets in variables or files.',
      appliesTo: ['Pipeline', 'Cloud', 'Kubernetes'],
      keywords: 'secrets management vault sops kms oidc credentials',
      builtins: [
        { platform: 'GitHub', text: 'Environment secrets with required reviewers, and OIDC federation to AWS, Azure, Google Cloud, and HashiCorp Vault.' },
        { platform: 'GitLab', text: 'the <code>secrets:</code> keyword reads from HashiCorp Vault, Azure Key Vault, or Google Secret Manager using an <code>id_tokens</code> JWT (Premium). On any tier, jobs can exchange an <code>id_tokens</code> JWT for short-lived cloud credentials.' },
      ],
      concepts: ['Secret zero', 'Short-lived credentials', 'Workload identity', 'Cloud secrets managers and KMS', 'Encryption at rest in git', 'Rotation'],
      tools: [
        {
          id: 'vault', name: 'HashiCorp Vault', pick: 'start', repo: 'hashicorp/vault', license: 'BUSL-1.1',
          docs: 'https://developer.hashicorp.com/vault/docs',
          role: 'Central secret store with dynamic credentials and JWT login for GitLab jobs.',
          gitlab: 'Native secrets: integration (Premium)',
          why: 'GitLab jobs log in with their OIDC token, so no secret is stored in GitLab at all. Vault can also mint short-lived database and cloud credentials per job.',
          caution: 'Vault is under the Business Source License. OpenBao (openbao/openbao) is an MPL-2.0 fork with a compatible API if you need an open-source license.',
          install: [
            { label: 'Homebrew', code: 'brew tap hashicorp/tap\nbrew install hashicorp/tap/vault' },
            { label: 'Development server (never use in production)', code: 'vault server -dev' },
          ],
          run: [{ label: 'Trust GitLab job tokens (JWT auth)', code: 'vault auth enable jwt\nvault write auth/jwt/config \\\n  oidc_discovery_url="https://gitlab.com" \\\n  bound_issuer="https://gitlab.com"' }],
          ci: `deploy:
  stage: deploy
  id_tokens:
    VAULT_ID_TOKEN:
      aud: https://vault.example.com
  secrets:
    DATABASE_PASSWORD:
      vault: production/db/password@ops   # path/field@mount
      token: $VAULT_ID_TOKEN
  variables:
    VAULT_SERVER_URL: https://vault.example.com
  script:
    - ./deploy.sh                          # DATABASE_PASSWORD is a file path`,
          results: 'Bind Vault roles to claims such as <code>project_path</code> and <code>ref_protected</code> so only protected branches of a given project can read production secrets.',
        },
        {
          id: 'sops', name: 'SOPS', repo: 'getsops/sops', license: 'MPL-2.0',
          docs: 'https://getsops.io/docs/',
          role: 'Encrypts values inside YAML, JSON, and env files so they can live in git.',
          why: 'Good for GitOps and small teams: secrets stay next to the code, encrypted with age, PGP, or a cloud KMS, and diffs remain readable.',
          install: [{ label: 'Homebrew', code: 'brew install sops age' }],
          run: [
            { label: 'Create a key and encrypt a file', code: 'age-keygen -o key.txt\nsops encrypt --age <public-key> secrets.yaml > secrets.enc.yaml' },
            { label: 'Decrypt', code: 'SOPS_AGE_KEY_FILE=key.txt sops decrypt secrets.enc.yaml' },
          ],
          ci: `decrypt:
  stage: deploy
  image: alpine:3.20
  before_script:
    - apk add --no-cache sops
  script:
    # SOPS_AGE_KEY is a protected, masked CI/CD variable
    - sops decrypt secrets.enc.yaml > secrets.yaml
    - ./deploy.sh`,
          results: 'Store the private key only in a protected variable or a KMS. Add a <code>.sops.yaml</code> creation rule so everyone encrypts with the same keys.',
        },
        {
          id: 'external-secrets', name: 'External Secrets Operator', repo: 'external-secrets/external-secrets', license: 'Apache-2.0',
          docs: 'https://external-secrets.io/',
          role: 'Syncs secrets from Vault or cloud secret managers into Kubernetes Secrets.',
          why: 'Applications keep reading normal Kubernetes Secrets while the source of truth stays in Vault, AWS, GCP, or Azure.',
          install: [{ label: 'Helm', code: 'helm repo add external-secrets https://charts.external-secrets.io\nhelm install external-secrets external-secrets/external-secrets \\\n  -n external-secrets --create-namespace' }],
          run: [{ label: 'Check that the operator is running', code: 'kubectl get pods -n external-secrets\nkubectl get secretstores,externalsecrets -A' }],
          results: 'Define a SecretStore per namespace and an ExternalSecret per application secret. Limit who can create SecretStores: they decide which vault paths a namespace can read.',
        },
      ],
    },
    {
      id: 'containers', phase: 'build', title: 'Container images',
      goal: 'Build small, non-root images from trusted bases and block images with critical vulnerabilities.',
      appliesTo: ['Containers'],
      keywords: 'docker dockerfile container image registry distroless',
      builtins: [
        { platform: 'GitHub', text: 'Code scanning shows SARIF results from Trivy, hadolint, and Dockle next to code findings.' },
        { platform: 'GitLab', text: '<code>include: - template: Jobs/Container-Scanning.gitlab-ci.yml</code> scans images with Trivy on every tier; results in the merge request need Ultimate.' },
      ],
      concepts: ['Dockerfile best practices', 'Golden and distroless base images', 'Non-root users', 'Linux capabilities', 'Namespaces and cgroups', 'Container escape', 'Registry hygiene'],
      tools: [
        {
          id: 'hadolint', name: 'hadolint', pick: 'start', repo: 'hadolint/hadolint', license: 'GPL-3.0',
          docs: 'https://github.com/hadolint/hadolint#readme',
          role: 'Dockerfile linter that also checks the shell commands inside RUN.',
          gitlab: 'Code quality report format',
          why: 'Catches unpinned base images, root users, and fragile shell in seconds, before anything is built. The easiest container check to add first.',
          caution: 'The default image has no shell. In GitLab use the <code>latest-debian</code> or <code>latest-alpine</code> tag. GitLab deprecated the codeclimate report format in 17.3; prefer SARIF if you collect results elsewhere.',
          install: [{ label: 'Homebrew or container', code: 'brew install hadolint\n# or\ndocker run --rm -i hadolint/hadolint < Dockerfile' }],
          run: [
            { label: 'Lint a Dockerfile', code: 'hadolint Dockerfile' },
            { label: 'SARIF output', code: 'hadolint -f sarif Dockerfile > hadolint.sarif' },
          ],
          ci: `hadolint:
  stage: test
  image: hadolint/hadolint:latest-debian
  script:
    - mkdir -p reports
    - hadolint -f gitlab_codeclimate Dockerfile > reports/hadolint.json
  artifacts:
    when: always
    reports:
      codequality: reports/hadolint.json`,
          results: 'Fails at or above <code>--failure-threshold</code> (default info). Ignore a reviewed rule inline with <code># hadolint ignore=DL3008</code>.',
        },
        {
          id: 'trivy-image', name: 'Trivy (image)', repo: 'aquasecurity/trivy', license: 'Apache-2.0',
          docs: 'https://trivy.dev/docs/latest/', repoPath: 'scanners/trivy',
          role: 'Scans built images for OS and library vulnerabilities, secrets, and misconfiguration.',
          gitlab: 'Container scanning report template included',
          why: 'This is what GitLab container scanning runs under the hood. Running it yourself gives you the same report on any tier and full control over thresholds.',
          caution: 'In March 2026 Trivy images on Docker Hub and its GitHub Actions were reported compromised. Pin <code>aquasec/trivy</code> by digest.',
          install: [{ label: 'Homebrew', code: 'brew install trivy' }],
          run: [
            { label: 'Scan an image', code: 'trivy image python:3.12-slim' },
            { label: 'Fail on critical findings', code: 'trivy image --exit-code 1 --severity CRITICAL my-app:latest' },
          ],
          ci: `container-scan:
  stage: test
  image:
    name: aquasec/trivy:latest          # pin by digest
    entrypoint: [""]
  variables:
    FULL_IMAGE_NAME: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    TRIVY_USERNAME: $CI_REGISTRY_USER
    TRIVY_PASSWORD: $CI_REGISTRY_PASSWORD
    TRIVY_AUTH_URL: $CI_REGISTRY
    TRIVY_NO_PROGRESS: "true"
  script:
    - trivy image --exit-code 0 --format template --template "@/contrib/gitlab.tpl"
        --output "$CI_PROJECT_DIR/gl-container-scanning-report.json" "$FULL_IMAGE_NAME"
    - trivy image --exit-code 1 --severity CRITICAL "$FULL_IMAGE_NAME"
  artifacts:
    when: always
    reports:
      container_scanning: gl-container-scanning-report.json`,
          results: 'The first command writes the GitLab report; the second fails the job on critical findings. Use <code>.trivyignore</code> with a reason for accepted CVEs.',
        },
        {
          id: 'dockle', name: 'Dockle', repo: 'goodwithtech/dockle', license: 'Apache-2.0',
          docs: 'https://github.com/goodwithtech/dockle#readme',
          role: 'Checks a built image against CIS Docker benchmark and best practices.',
          why: 'Complements vulnerability scanning: finds root users, setuid files, secrets in environment variables, and missing health checks.',
          install: [{ label: 'Homebrew', code: 'brew install goodwithtech/r/dockle' }],
          run: [{ label: 'Check an image, fail on warnings', code: 'dockle --exit-code 1 --exit-level warn my-app:latest' }],
          ci: `dockle:
  stage: test
  image:
    name: goodwithtech/dockle:latest
    entrypoint: [""]
  variables:
    DOCKLE_USERNAME: $CI_REGISTRY_USER
    DOCKLE_PASSWORD: $CI_REGISTRY_PASSWORD
  script:
    - dockle -f sarif -o dockle.sarif --exit-code 1 "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA"
  artifacts:
    when: always
    paths: [dockle.sarif]`,
          results: 'Exits 0 by default even with findings; <code>--exit-code 1</code> fails on WARN and FATAL. Skip a reviewed check with <code>-i CIS-DI-0001</code>.',
        },
        {
          id: 'distroless', name: 'distroless base images', repo: 'GoogleContainerTools/distroless', license: 'Apache-2.0',
          docs: 'https://github.com/GoogleContainerTools/distroless#readme', repoPath: 'policies/containers/distroless-examples',
          role: 'Minimal base images with no shell or package manager.',
          why: 'Removing the shell and package manager removes most of what an attacker would use after a break-in, and most of the CVEs scanners report.',
          install: [{ label: 'Use as the final stage of a multi-stage build', code: 'FROM golang:1.23 AS build\nWORKDIR /src\nCOPY . .\nRUN CGO_ENABLED=0 go build -o /app .\n\nFROM gcr.io/distroless/static-debian12:nonroot\nCOPY --from=build /app /app\nUSER nonroot\nENTRYPOINT ["/app"]', lang: 'docker' }],
          results: 'Debug with the <code>:debug</code> tags, which add a busybox shell; never ship them to production. Reference Dockerfiles for other languages are in this repository.',
        },
        {
          id: 'skopeo', name: 'skopeo', repo: 'podman-container-tools/skopeo', license: 'Apache-2.0',
          docs: 'https://github.com/podman-container-tools/skopeo#readme',
          role: 'Inspects and copies images between registries and archives without a Docker daemon.',
          why: 'Lets scanners pull an image as a file in CI without Docker-in-Docker or privileged runners, then scan the archive.',
          install: [{ label: 'Homebrew', code: 'brew install skopeo' }],
          run: [
            { label: 'Inspect an image and read its digest', code: "skopeo inspect docker://nginx:1.25 | jq '.Digest'" },
            { label: 'Save an image as an OCI archive for scanning', code: 'skopeo copy docker://nginx:1.25 oci-archive:nginx.tar' },
          ],
          results: 'Uses credentials from <code>skopeo login</code>, <code>docker login</code>, or <code>--creds</code>.',
        },
        {
          id: 'crane', name: 'crane', repo: 'google/go-containerregistry', license: 'Apache-2.0',
          docs: 'https://github.com/google/go-containerregistry/tree/main/cmd/crane',
          role: 'Small CLI for registry operations: digests, tags, manifests, and filesystem export.',
          why: 'Resolve tags to digests for pinning, list tags, and export an image filesystem for malware or secret scans.',
          install: [{ label: 'Homebrew or Go', code: 'brew install crane\n# or\ngo install github.com/google/go-containerregistry/cmd/crane@latest' }],
          run: [
            { label: 'Resolve a tag to a digest', code: 'crane digest nginx:1.25' },
            { label: 'Export the image filesystem', code: 'mkdir rootfs && crane export nginx:1.25 - | tar -x -C rootfs' },
          ],
        },
      ],
    },
    {
      id: 'iac', phase: 'build', title: 'Infrastructure as code',
      goal: 'Check Terraform, Helm, and Kubernetes manifests before anything is applied.',
      appliesTo: ['Code', 'Cloud', 'Kubernetes'],
      keywords: 'iac terraform helm kubernetes manifests policy as code rego',
      builtins: [
        { platform: 'GitLab', text: '<code>include: - template: Jobs/SAST-IaC.gitlab-ci.yml</code> runs KICS on every tier; merge request findings need Ultimate.' },
      ],
      concepts: ['Policy as code', 'Terraform plan vs source scans', 'Terraform state secrets', 'Secure configuration baseline', 'Version-controlled configuration', 'Drift'],
      tools: [
        {
          id: 'checkov', name: 'Checkov', pick: 'start', repo: 'bridgecrewio/checkov', license: 'Apache-2.0',
          docs: 'https://www.checkov.io/1.Welcome/Quick%20Start.html', repoPath: 'policies/terraform',
          role: 'Over a thousand checks for Terraform, Helm, Kubernetes, CloudFormation, and Dockerfiles.',
          gitlab: 'GitLab SAST output',
          why: 'Broadest coverage in one tool, with checks for Terraform plans (resolved values) as well as source. Custom policies can be written in YAML.',
          install: [{ label: 'pip or Homebrew', code: 'pip3 install checkov\n# or\nbrew install checkov' }],
          run: [
            { label: 'Scan a directory', code: 'checkov -d .' },
            { label: 'Scan a Terraform plan', code: 'terraform plan -out tf.plan\nterraform show -json tf.plan > tf.json\ncheckov -f tf.json' },
          ],
          ci: `checkov:
  stage: test
  image:
    name: bridgecrew/checkov:latest
    entrypoint: [""]
  script:
    - checkov -d . -o cli -o junitxml --output-file-path console,checkov.xml
  artifacts:
    when: always
    reports:
      junit: checkov.xml`,
          results: 'Failed checks fail the job; use <code>--soft-fail</code> while you tune, and <code>--skip-check CKV_AWS_20</code> or an inline <code>#checkov:skip=CKV_AWS_20:reason</code> for accepted risks.',
        },
        {
          id: 'kics', name: 'KICS', repo: 'Checkmarx/kics', license: 'Apache-2.0',
          docs: 'https://docs.kics.io/',
          role: 'Rego queries for Terraform, Helm, Docker, Ansible, and more; behind GitLab IaC SAST.',
          gitlab: 'GitLab SAST output (glsast)',
          why: 'The engine GitLab uses for IaC scanning. Running it directly lets you pick report formats and severity gates.',
          caution: 'In March and April 2026 KICS GitHub Actions and Docker Hub images were reported compromised. Pin by digest and verify.',
          install: [{ label: 'Container image', code: 'docker pull checkmarx/kics:latest' }],
          run: [{ label: 'Scan a directory', code: 'docker run -t -v "$PWD":/path checkmarx/kics scan -p /path -o /path/' }],
          ci: `kics:
  stage: test
  image:
    name: checkmarx/kics:latest        # pin by digest
    entrypoint: [""]
  script:
    - kics scan -p "$CI_PROJECT_DIR" --ignore-on-exit all
        --report-formats glsast -o "$CI_PROJECT_DIR" --output-name kics-results
  artifacts:
    reports:
      sast: gl-sast-kics-results.json`,
          results: 'Exit codes encode the highest severity found (60 critical, 50 high, 40 medium, 30 low); <code>--fail-on high</code> and <code>--ignore-on-exit</code> control gating.',
        },
        {
          id: 'conftest', name: 'conftest', repo: 'open-policy-agent/conftest', license: 'Apache-2.0',
          docs: 'https://www.conftest.dev/', repoPath: 'policies/terraform/conftest-examples',
          role: 'Tests any structured config file against your own Rego policies.',
          why: 'For rules specific to your organization: required labels, allowed registries, naming. The same Rego works for Terraform, Kubernetes YAML, and Dockerfiles.',
          install: [{ label: 'Homebrew or Go', code: 'brew install conftest\n# or\nCGO_ENABLED=0 go install github.com/open-policy-agent/conftest@latest' }],
          run: [
            { label: 'Test a manifest against a policy directory', code: 'conftest test -p policy/ deployment.yaml' },
            { label: 'Terraform with the HCL2 parser', code: 'conftest test -p policy/ main.tf --parser hcl2' },
          ],
          ci: `conftest:
  stage: test
  image:
    name: openpolicyagent/conftest:latest
    entrypoint: [""]
  script:
    - conftest test -p policy/ k8s/ --output junit > conftest.xml
  artifacts:
    when: always
    reports:
      junit: conftest.xml`,
          results: 'Exit code 1 when a <code>deny</code> rule fails; with <code>--fail-on-warn</code> warnings exit 1 and failures exit 2.',
        },
        {
          id: 'trivy-config', name: 'Trivy (config)', repo: 'aquasecurity/trivy', license: 'Apache-2.0',
          docs: 'https://trivy.dev/docs/latest/',
          role: 'Misconfiguration checks for IaC with the same binary you use for images.',
          why: 'Avoids adding another tool if Trivy already runs in your pipeline. It replaced the separate tfsec project.',
          install: [{ label: 'Homebrew', code: 'brew install trivy' }],
          run: [{ label: 'Scan IaC with SARIF output', code: 'trivy config --format sarif -o trivy-iac.sarif .' }],
          results: 'Add <code>--exit-code 1 --severity HIGH,CRITICAL</code> to gate.',
        },
        {
          id: 'terraform-compliance', name: 'terraform-compliance', repo: 'terraform-compliance/cli', license: 'MIT',
          docs: 'https://terraform-compliance.com',
          role: 'Readable BDD scenarios that a Terraform plan must satisfy.',
          why: 'Lets security and compliance teams write rules in plain Given/When/Then sentences that engineers can read and review.',
          install: [{ label: 'pip', code: 'pip install terraform-compliance' }],
          run: [{ label: 'Check a plan against feature files', code: 'terraform show -json plan.out > plan.out.json\nterraform-compliance -f features/ -p plan.out.json' }],
          results: 'Failed scenarios exit non-zero; <code>--no-failures</code> forces 0 while you introduce rules.',
        },
      ],
    },
    /* ------------------------------------------------------------------ PHASE 3 */
    {
      id: 'supply', phase: 'ship', title: 'SBOM, signing, and provenance',
      goal: 'Record what every release contains, sign it, and prove where it was built.',
      appliesTo: ['Pipeline', 'Containers'],
      keywords: 'sbom cyclonedx spdx signing cosign sigstore provenance slsa attestation supply chain',
      builtins: [
        { platform: 'GitHub', text: 'Artifact attestations (<code>actions/attest-build-provenance</code>) create signed SLSA provenance; free for public repositories, private repositories need GitHub Enterprise Cloud.' },
        { platform: 'GitLab', text: '<code>artifacts:reports:cyclonedx</code> shows SBOMs in the dependency list (Ultimate), and setting <code>RUNNER_GENERATE_ARTIFACTS_METADATA: "true"</code> makes runners write SLSA provenance for job artifacts.' },
      ],
      concepts: ['Software supply chain', 'SBOM: CycloneDX and SPDX', 'Artifact repository', 'Artifact signing', 'Keyless signing with OIDC', 'Provenance and SLSA levels', 'Artifact integrity'],
      tools: [
        {
          id: 'syft', name: 'syft', pick: 'start', repo: 'anchore/syft', license: 'Apache-2.0',
          docs: 'https://oss.anchore.com/docs/guides/sbom/getting-started/',
          role: 'Generates CycloneDX or SPDX SBOMs from images and directories.',
          gitlab: 'CycloneDX report for GitLab',
          why: 'Fast, accurate, and covers dozens of ecosystems. Generate one SBOM per release and feed it to Grype, Dependency-Track, and GitLab.',
          install: [{ label: 'Install script', code: 'curl -sSfL https://get.anchore.io/syft | sudo sh -s -- -b /usr/local/bin' }],
          run: [
            { label: 'SBOM for an image', code: 'syft my-app:latest -o cyclonedx-json=sbom.cdx.json' },
            { label: 'Two formats at once', code: 'syft ./ -o spdx-json=sbom.spdx.json -o cyclonedx-json=sbom.cdx.json' },
          ],
          ci: `sbom:
  stage: build
  image: alpine:3.20                 # the official image has no shell
  before_script:
    - apk add --no-cache curl
    - curl -sSfL https://get.anchore.io/syft | sh -s -- -b /usr/local/bin
  script:
    - syft dir:. -o cyclonedx-json=gl-sbom.cdx.json
  artifacts:
    paths: [gl-sbom.cdx.json]
    reports:
      cyclonedx: gl-sbom.cdx.json`,
          results: 'Keep the SBOM with the release artifact. Score its completeness with sbomqs and scan it with Grype.',
        },
        {
          id: 'cdxgen', name: 'cdxgen', repo: 'cdxgen/cdxgen', license: 'Apache-2.0',
          docs: 'https://cdxgen.github.io/cdxgen',
          role: 'CycloneDX generator from source code, with deep language support.',
          why: 'Builds richer SBOMs from source than image scanners can, including dependency trees and evidence. Good for polyglot repositories.',
          install: [{ label: 'npm or Homebrew', code: 'npm install -g @cdxgen/cdxgen --ignore-scripts\n# or\nbrew install cdxgen' }],
          run: [{ label: 'Recursive SBOM for a repository', code: 'cdxgen -r -o bom.json .' }],
          ci: `cdxgen:
  stage: build
  image:
    name: ghcr.io/cdxgen/cdxgen:master
    entrypoint: [""]
  script:
    - cdxgen -r -o bom.json .
  artifacts:
    paths: [bom.json]
    reports:
      cyclonedx: bom.json`,
          results: 'The npm package was renamed from <code>@cyclonedx/cdxgen</code> to <code>@cdxgen/cdxgen</code>; update old install commands.',
        },
        {
          id: 'cosign', name: 'cosign', pick: 'start', repo: 'sigstore/cosign', license: 'Apache-2.0',
          docs: 'https://docs.sigstore.dev/cosign/signing/overview/', repoPath: 'policies/supply-chain/sigstore-policy-controller',
          role: 'Signs and verifies images and files; keyless with the GitLab job identity.',
          gitlab: 'Keyless signing with id_tokens',
          why: 'Keyless signing ties each signature to the exact GitLab project and branch that built the image, with no key to store or rotate.',
          install: [{ label: 'Homebrew or Alpine', code: 'brew install cosign\n# in CI\napk add --no-cache cosign' }],
          run: [{ label: 'Verify an image signed by a GitLab pipeline', code: 'cosign verify "$IMAGE" \\\n  --certificate-identity "https://gitlab.com/my-group/my-project//.gitlab-ci.yml@refs/heads/main" \\\n  --certificate-oidc-issuer "https://gitlab.com"' }],
          ci: `sign-image:
  stage: deploy
  image: docker:27
  services: [docker:27-dind]
  id_tokens:
    SIGSTORE_ID_TOKEN:
      aud: sigstore
  variables:
    COSIGN_YES: "true"
  before_script:
    - apk add --no-cache cosign
    - docker login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
  script:
    - IMAGE_DIGEST=$(docker inspect --format='{{index .RepoDigests 0}}' "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA")
    - cosign sign "$IMAGE_DIGEST"
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`,
          results: 'Always sign by digest, not by tag. Enforce signatures at deploy with the Sigstore policy-controller or Kyverno <code>verifyImages</code>.',
        },
        {
          id: 'slsa-github-generator', name: 'SLSA GitHub generator', repo: 'slsa-framework/slsa-github-generator', license: 'Apache-2.0',
          docs: 'https://github.com/slsa-framework/slsa-github-generator#readme',
          role: 'Reusable workflows that produce SLSA Build Level 3 provenance on GitHub Actions.',
          gitlab: 'GitHub Actions only',
          why: 'Provenance is generated in an isolated reusable workflow, so the build job cannot forge it. Consumers verify it with slsa-verifier.',
          github: `jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      hashes: \${{ steps.hash.outputs.hashes }}
    steps:
      - uses: actions/checkout@v7          # pin to a commit SHA
      - run: make build
      - id: hash
        run: echo "hashes=$(sha256sum dist/* | base64 -w0)" >> "$GITHUB_OUTPUT"
  provenance:
    needs: [build]
    permissions:
      actions: read
      id-token: write
      contents: write
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_generic_slsa3.yml@v2.1.0
    with:
      base64-subjects: "\${{ needs.build.outputs.hashes }}"`,
          results: 'Reusable workflows must be referenced by tag (for example <code>@v2.1.0</code>), not by SHA; that is how the verifier identifies the builder.',
        },
        {
          id: 'slsa-verifier', name: 'slsa-verifier', repo: 'slsa-framework/slsa-verifier', license: 'Apache-2.0',
          docs: 'https://github.com/slsa-framework/slsa-verifier#readme',
          role: 'Verifies SLSA provenance before you install or deploy an artifact.',
          gitlab: 'Provenance from the SLSA GitHub generator and Google Cloud Build',
          why: 'Closes the loop: a release is only trusted if its provenance proves it was built from the expected repository and branch.',
          caution: 'It does not verify provenance produced by GitLab CI or Bitbucket Pipelines.',
          install: [{ label: 'Go', code: 'go install github.com/slsa-framework/slsa-verifier/v2/cli/slsa-verifier@v2.7.1' }],
          run: [{ label: 'Verify an artifact', code: 'slsa-verifier verify-artifact my-app-linux-amd64 \\\n  --provenance-path my-app-linux-amd64.intoto.jsonl \\\n  --source-uri github.com/my-org/my-app' }],
          results: 'Prints <code>PASSED: Verified SLSA provenance</code> on success.',
        },
        {
          id: 'witness', name: 'witness', repo: 'in-toto/witness', license: 'Apache-2.0',
          docs: 'https://witness.dev',
          role: 'Wraps build steps and produces signed in-toto attestations.',
          why: 'Captures evidence about how each step ran (environment, materials, products) and verifies the whole chain against a policy.',
          caution: 'Its GitLab attestor documentation still relies on <code>CI_JOB_JWT</code>, which GitLab removed in 17.0. Test it on your GitLab version before relying on it.',
          install: [{ label: 'Install script', code: 'bash <(curl -s https://raw.githubusercontent.com/in-toto/witness/main/install-witness.sh)' }],
          run: [
            { label: 'Attest a build step', code: 'witness run -s build -a environment -k buildkey.pem -o build-attestation.json -- make build' },
            { label: 'Verify against a policy', code: 'witness verify -p policy-signed.json -a build-attestation.json -k policypub.pem -f ./app' },
          ],
          results: '<code>witness verify</code> exits 0 only when every attestation required by the policy is present and valid.',
        },
        {
          id: 'sbomqs', name: 'sbomqs', repo: 'interlynk-io/sbomqs', license: 'Apache-2.0',
          docs: 'https://github.com/interlynk-io/sbomqs/tree/main/docs',
          role: 'Scores SBOM quality and checks it against standards such as BSI and NTIA.',
          why: 'An SBOM with missing versions or suppliers is of little use. Gate releases on a minimum quality score.',
          install: [{ label: 'Homebrew or Go', code: 'brew tap interlynk-io/interlynk && brew install sbomqs\n# or\ngo install github.com/interlynk-io/sbomqs/v2@latest' }],
          run: [{ label: 'Score an SBOM', code: 'sbomqs score sbom.cdx.json\nsbomqs score sbom.cdx.json --json' }],
          results: '<code>score</code> does not fail on its own. Gate with jq in the job script; check the JSON field name for your version, because the docs show both <code>avg_score</code> and <code>sbom_quality_score</code>.',
        },
      ],
    },
    {
      id: 'k8s', phase: 'ship', title: 'Kubernetes admission and audit',
      goal: 'Reject unsafe workloads at the cluster door and audit clusters against benchmarks.',
      appliesTo: ['Kubernetes'],
      keywords: 'kubernetes k8s admission policy kyverno gatekeeper opa pod security cis',
      concepts: ['Admission control', 'Pod Security Standards', 'RBAC', 'Network policies', 'Audit first, then enforce', 'Managed Kubernetes', 'GitOps'],
      tools: [
        {
          id: 'kyverno', name: 'Kyverno', pick: 'start', repo: 'kyverno/kyverno', license: 'Apache-2.0',
          docs: 'https://kyverno.io/docs/', repoPath: 'policies/kubernetes/kyverno-policies',
          role: 'Admission controller with policies written as Kubernetes YAML or CEL.',
          why: 'No new language to learn, and the full community policy library is imported in this repository. The CLI tests the same policies in CI before they reach a cluster.',
          caution: 'The Kyverno CLI image has no shell; install the CLI in a shell image for GitLab jobs.',
          install: [{ label: 'Controller (Helm)', code: 'helm repo add kyverno https://kyverno.github.io/kyverno/\nkubectl create namespace kyverno\nhelm install kyverno --namespace kyverno kyverno/kyverno' }],
          run: [
            { label: 'Apply policies to manifests offline', code: 'kyverno apply policies/ --resource k8s/deployment.yaml' },
            { label: 'Run policy tests (kyverno-test.yaml)', code: 'kyverno test .' },
          ],
          results: 'Start every policy with <code>validationFailureAction: Audit</code>, read the PolicyReports, then switch to <code>Enforce</code>. Test policies against a live cluster with Chainsaw.',
        },
        {
          id: 'chainsaw', name: 'Chainsaw', repo: 'kyverno/chainsaw', license: 'Apache-2.0',
          docs: 'https://kyverno.github.io/chainsaw/latest/',
          role: 'End-to-end tests for policies and controllers against a real cluster.',
          why: 'Proves a policy actually blocks what it should, in a kind cluster in CI, before you enforce it in production.',
          install: [{ label: 'Homebrew (use the tap; core has an unrelated chainsaw)', code: 'brew tap kyverno/chainsaw https://github.com/kyverno/chainsaw\nbrew install kyverno/chainsaw/chainsaw' }],
          run: [{ label: 'Run the tests in the current directory', code: 'chainsaw test' }],
          results: 'Write JUnit with <code>--report-format JUNIT-TEST</code> to show results in GitLab.',
        },
        {
          id: 'gatekeeper', name: 'Gatekeeper', repo: 'open-policy-agent/gatekeeper', license: 'Apache-2.0',
          docs: 'https://open-policy-agent.github.io/gatekeeper/website/docs/', repoPath: 'policies/kubernetes/gatekeeper-library',
          role: 'OPA-based admission controller with Rego constraint templates.',
          why: 'Choose it if your team already writes Rego for OPA or conftest. The constraint template library is imported in this repository.',
          install: [
            { label: 'Controller (Helm)', code: 'helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts\nhelm install gatekeeper/gatekeeper --name-template=gatekeeper \\\n  --namespace gatekeeper-system --create-namespace' },
            { label: 'gator CLI', code: 'brew install gator' },
          ],
          run: [
            { label: 'Test manifests against templates and constraints', code: 'gator test -f=my-manifest.yaml -f=templates-and-constraints/' },
            { label: 'Run test suites', code: 'gator verify ./...' },
          ],
          results: '<code>gator test</code> exits 1 on violations of constraints with <code>enforcementAction: deny</code>; <code>dryrun</code> constraints only report.',
        },
        {
          id: 'kube-linter', name: 'kube-linter', repo: 'stackrox/kube-linter', license: 'Apache-2.0',
          docs: 'https://docs.kubelinter.io',
          role: 'Static checks for manifests and Helm charts before deploy.',
          why: 'Catches privileged containers, missing limits, and writable root filesystems in the merge request, without a cluster.',
          install: [{ label: 'Homebrew or Go', code: 'brew install kube-linter\n# or\ngo install golang.stackrox.io/kube-linter/cmd/kube-linter@latest' }],
          run: [{ label: 'Lint with SARIF output', code: 'kube-linter lint --format sarif --output kube-linter.sarif k8s/' }],
          ci: `kube-linter:
  stage: test
  image:
    name: stackrox/kube-linter:latest-alpine   # the default tag has no shell
    entrypoint: [""]
  script:
    - /kube-linter lint --format sarif --output kube-linter.sarif k8s/
  artifacts:
    when: always
    paths: [kube-linter.sarif]`,
          results: 'Exits non-zero when a check fails. Tune checks in <code>.kube-linter.yaml</code>.',
        },
        {
          id: 'kubescape', name: 'Kubescape', repo: 'kubescape/kubescape', license: 'Apache-2.0',
          docs: 'https://kubescape.io/docs/',
          role: 'Scans manifests and clusters against NSA, MITRE, and CIS frameworks.',
          gitlab: 'Upstream GitLab CI guide; GitLab SAST output',
          why: 'Gives a compliance-style score per framework and works both on files in CI and on live clusters.',
          install: [{ label: 'Homebrew or script', code: 'brew install kubescape\n# or\ncurl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash' }],
          run: [
            { label: 'Scan manifests', code: 'kubescape scan k8s/' },
            { label: 'Scan the current cluster against NSA guidance', code: 'kubescape scan framework nsa --compliance-threshold 80' },
          ],
          ci: `kubescape:
  stage: test
  image: alpine:3.20
  before_script:
    - apk add --no-cache bash curl gcompat
    - curl -s https://raw.githubusercontent.com/kubescape/kubescape/master/install.sh | /bin/bash
    - export PATH=$PATH:$HOME/.kubescape/bin
  script:
    - kubescape scan . --format gitlab-sast --output gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json`,
          results: 'Exit code 1 when <code>--compliance-threshold</code> or <code>--severity-threshold</code> is not met.',
        },
        {
          id: 'kube-bench', name: 'kube-bench', repo: 'aquasecurity/kube-bench', license: 'Apache-2.0',
          docs: 'https://github.com/aquasecurity/kube-bench/blob/main/docs/running.md',
          role: 'Checks cluster nodes against the CIS Kubernetes Benchmark.',
          why: 'The standard evidence for a CIS audit of your clusters. Platform-specific jobs exist for EKS, GKE, and AKS.',
          install: [{ label: 'Run as a Job in the cluster', code: 'kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml\nkubectl logs job/kube-bench' }],
          run: [{ label: 'Use the job for your platform', code: '# job-eks.yaml, job-gke.yaml, job-aks.yaml in the repository' }],
          results: 'Results are in the pod logs; edit the job command to <code>["kube-bench", "--json"]</code> for machine-readable output. <code>--exit-code</code> makes FAIL results return a non-zero code.',
        },
      ],
    },
    /* ------------------------------------------------------------------ PHASE 4 */
    {
      id: 'dast', phase: 'run', title: 'Dynamic testing (DAST)',
      goal: 'Attack the running application and API in a test environment, the way an outsider would.',
      appliesTo: ['Running apps'],
      keywords: 'dast dynamic testing zap nuclei api fuzzing openapi web',
      builtins: [
        { platform: 'GitLab', text: '<code>include: - template: DAST.gitlab-ci.yml</code> requires GitLab Ultimate. The open-source scanners below work on any tier.' },
      ],
      concepts: ['OWASP Top 10', 'Security headers: CSP, Referrer-Policy, Permissions-Policy', 'XSS and CSRF', 'SSRF', 'API schema exposure', 'Rate limits', 'Fuzz testing'],
      tools: [
        {
          id: 'zap', name: 'OWASP ZAP', pick: 'start', repo: 'zaproxy/zaproxy', license: 'Apache-2.0',
          docs: 'https://www.zaproxy.org/docs/docker/baseline-scan/', repoPath: 'scanners/zap',
          role: 'Web and API scanner with ready baseline, full, and OpenAPI scan scripts.',
          why: 'The baseline scan is passive and safe to run against staging on every deploy. The API scan imports your OpenAPI spec so every endpoint gets tested.',
          caution: 'Scan only environments you are authorized to test. The full scan sends attacks and can change data.',
          install: [{ label: 'Container image', code: 'docker pull ghcr.io/zaproxy/zaproxy:stable' }],
          run: [
            { label: 'Passive baseline scan', code: 'docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \\\n  zap-baseline.py -t https://staging.example.com -r report.html -J report.json' },
            { label: 'API scan from an OpenAPI spec', code: 'docker run -v $(pwd):/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \\\n  zap-api-scan.py -t https://staging.example.com/openapi.json -f openapi -r api.html -J api.json' },
          ],
          ci: `zap-baseline:
  stage: dast
  image: ghcr.io/zaproxy/zaproxy:stable
  variables:
    TARGET_URL: https://staging.example.com
  script:
    - mkdir -p /zap/wrk
    - zap-baseline.py -t "$TARGET_URL" -r report.html -J report.json -I || true
    - cp /zap/wrk/report.* "$CI_PROJECT_DIR"/
  artifacts:
    when: always
    paths: [report.html, report.json]
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`,
          results: 'Exit codes: 0 pass, 1 at least one FAIL, 2 warnings only, 3 other error; <code>-I</code> does not fail on warnings. Tune rules with a config file generated by <code>-g</code>. There is no SARIF option; import JSON into DefectDojo.',
        },
        {
          id: 'nuclei', name: 'nuclei', repo: 'projectdiscovery/nuclei', license: 'MIT',
          docs: 'https://docs.projectdiscovery.io/tools/nuclei/overview', repoPath: 'scanners/nuclei',
          role: 'Template-driven checks for exposures, misconfigurations, and known CVEs.',
          why: 'Thousands of community templates, and templates are simple YAML, so writing one for your own API takes minutes.',
          install: [{ label: 'Go', code: 'go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest' }],
          run: [
            { label: 'Scan a target', code: 'nuclei -target https://staging.example.com' },
            { label: 'SARIF output', code: 'nuclei -u https://staging.example.com -sarif-export nuclei.sarif' },
          ],
          ci: `nuclei:
  stage: dast
  image:
    name: projectdiscovery/nuclei:latest
    entrypoint: [""]
  script:
    - nuclei -u "$TARGET_URL" -severity medium,high,critical -sarif-export nuclei.sarif
  artifacts:
    when: always
    paths: [nuclei.sarif]`,
          results: 'nuclei does not fail on findings by itself; gate on the report in a later job.',
        },
        {
          id: 'schemathesis', name: 'Schemathesis', repo: 'schemathesis/schemathesis', license: 'MIT',
          docs: 'https://schemathesis.readthedocs.io/en/stable/',
          role: 'Property-based API tests generated from OpenAPI or GraphQL schemas.',
          gitlab: 'Upstream GitLab CI guide',
          why: 'Finds crashes, schema violations, and auth bypasses by generating thousands of valid and invalid requests from the spec you already have.',
          install: [{ label: 'uv or pip', code: 'uv tool install schemathesis\n# or\npip install schemathesis' }],
          run: [{ label: 'Test an API from its schema', code: 'schemathesis run https://staging.example.com/openapi.json --report junit' }],
          ci: `schemathesis:
  stage: dast
  image:
    name: schemathesis/schemathesis:stable
    entrypoint: [""]
  script:
    - schemathesis run "$TARGET_URL/openapi.json"
        --header "Authorization: Bearer $API_TOKEN"
        --wait-for-schema 60 --report junit
  artifacts:
    when: always
    reports:
      junit: schemathesis-report/junit-*.xml`,
          results: 'Exit code 1 when a check fails, 2 when the schema could not be loaded.',
        },
        {
          id: 'restler', name: 'RESTler', repo: 'microsoft/restler-fuzzer', license: 'MIT',
          docs: 'https://github.com/microsoft/restler-fuzzer/tree/main/docs/user-guide',
          role: 'Stateful REST API fuzzer that learns dependencies between requests.',
          why: 'Goes deeper than schema-based testing: it creates a resource, then uses its ID in later calls, finding bugs that only appear in sequences.',
          install: [{ label: 'Build locally (Python 3.12 and .NET 8 required)', code: 'python ./build-restler.py --dest_dir <path-to-restler-bin>' }],
          run: [{ label: 'Compile the spec, smoke-test, then fuzz', code: 'restler compile --api_spec openapi.json\nrestler test --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json\nrestler fuzz-lean --grammar_file Compile/grammar.py --dictionary_file Compile/dict.json --settings Compile/engine_settings.json' }],
          results: 'Bugs are written to <code>bug_buckets/bug_buckets.txt</code> under the results folder. Run it on schedule rather than on every merge request.',
        },
        {
          id: 'dalfox', name: 'Dalfox', repo: 'hahwul/dalfox', license: 'MIT',
          docs: 'https://dalfox.hahwul.com/',
          role: 'Fast scanner focused on reflected, stored, and DOM XSS.',
          why: 'Goes deeper on XSS than general scanners and verifies payloads. Feed it the endpoints from your OpenAPI spec.',
          install: [{ label: 'Homebrew or Snap', code: 'brew install dalfox\n# or\nsudo snap install dalfox' }],
          run: [{ label: 'Scan a URL', code: 'dalfox scan https://staging.example.com/search?q=test' }],
          results: 'DefectDojo has no Dalfox parser; convert results to the Generic Findings Import format to track them there.',
        },
        {
          id: 'burp', name: 'Burp Suite', license: 'Commercial; free Community Edition',
          docs: 'https://portswigger.net/burp/documentation',
          role: 'Intercepting proxy and scanner for manual web and API testing.',
          why: 'The standard tool for manual testing and verifying scanner findings. The Professional edition adds the automated scanner and extensions such as an MCP server for AI-assisted testing.',
          install: [{ label: 'Download', code: '# https://portswigger.net/burp/communitydownload' }],
          results: 'Use it to confirm or dismiss findings from automated DAST before they reach developers.',
        },
      ],
    },
    {
      id: 'mobile', phase: 'run', title: 'Mobile app builds',
      goal: 'Check the built APK and IPA for what source scans cannot see: debug flags, embedded secrets, exported components.',
      appliesTo: ['Code', 'Running apps'],
      keywords: 'mobile android ios apk ipa mobsf masvs',
      concepts: ['OWASP MASVS and MASTG', 'Decompilation', 'Exported components', 'Certificate pinning', 'Root and jailbreak detection', 'Obfuscation'],
      tools: [
        {
          id: 'mobsf', name: 'MobSF', pick: 'start', repo: 'MobSF/Mobile-Security-Framework-MobSF', license: 'GPL-3.0',
          docs: 'https://mobsf.github.io/docs', repoPath: 'scanners/mobsf',
          role: 'Static and dynamic analysis of APK, AAB, and IPA files with a REST API.',
          why: 'The standard open-source mobile analyzer. Run it as a service and let the pipeline upload each release build for analysis.',
          install: [{ label: 'Run the server', code: 'docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest' }],
          run: [{ label: 'Upload, scan, and fetch the JSON report', code: 'HASH=$(curl -s -F "file=@app.apk" -H "Authorization: $MOBSF_API_KEY" \\\n  http://localhost:8000/api/v1/upload | jq -r .hash)\ncurl -s -X POST -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" http://localhost:8000/api/v1/scan > /dev/null\ncurl -s -X POST -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" http://localhost:8000/api/v1/report_json > mobsf.json' }],
          ci: `mobsf:
  stage: test
  image: alpine:3.20
  variables:
    MOBSF_URL: https://mobsf.internal.example.com
  before_script:
    - apk add --no-cache curl jq
  script:
    - HASH=$(curl -s -F "file=@build/app-release.apk" -H "Authorization: $MOBSF_API_KEY" "$MOBSF_URL/api/v1/upload" | jq -r .hash)
    - curl -s -X POST -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" "$MOBSF_URL/api/v1/scan" > /dev/null
    - curl -s -X POST -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" "$MOBSF_URL/api/v1/report_json" > mobsf.json
  artifacts:
    when: always
    paths: [mobsf.json]`,
          results: 'The API key comes from the <code>MOBSF_API_KEY</code> environment variable of the server. Change the default UI credentials (mobsf/mobsf) on any shared instance.',
        },
        {
          id: 'apkleaks', name: 'apkleaks', repo: 'dwisiswant0/apkleaks', license: 'Apache-2.0',
          docs: 'https://github.com/dwisiswant0/apkleaks', repoPath: 'rules/secrets/apkleaks',
          role: 'Finds URLs, endpoints, and secrets inside an APK.',
          why: 'A quick check that release builds do not carry API keys or internal URLs. Its patterns are imported in this repository.',
          install: [{ label: 'pip', code: 'pip3 install apkleaks' }],
          run: [{ label: 'Scan an APK to JSON', code: 'apkleaks -f app-release.apk -o apkleaks.json --json' }],
          results: 'Needs jadx and offers to download it. There is no findings-based exit code, so review the report or gate with jq.',
        },
        {
          id: 'jadx', name: 'jadx', repo: 'skylot/jadx', license: 'Apache-2.0',
          docs: 'https://github.com/skylot/jadx/wiki',
          role: 'Decompiles APK and DEX files to readable Java for manual review.',
          why: 'Lets you review what is really inside a release build and run Semgrep rules on the decompiled code.',
          install: [{ label: 'Homebrew', code: 'brew install jadx' }],
          run: [{ label: 'Decompile an APK', code: 'jadx -d out app.apk' }],
        },
        {
          id: 'apktool', name: 'Apktool', repo: 'iBotPeaches/Apktool', license: 'Apache-2.0',
          docs: 'https://apktool.org',
          role: 'Decodes APK resources and AndroidManifest.xml.',
          why: 'Needed to inspect the final merged manifest: exported components, debuggable and backup flags, network security config.',
          install: [{ label: 'Download from the project site', code: '# see https://apktool.org for the wrapper script and jar' }],
          run: [{ label: 'Decode an APK', code: 'apktool d app.apk -o app_out' }],
        },
      ],
    },
    {
      id: 'cloud', phase: 'run', title: 'Cloud posture (CSPM)',
      goal: 'Scan AWS, Azure, and Google Cloud accounts for public data, missing encryption and logging, and drift from benchmarks such as CIS and PCI DSS.',
      appliesTo: ['Cloud'],
      keywords: 'cloud aws gcp azure cspm iam prowler compliance pci cis',
      concepts: ['IAM and least privilege', 'Cloud activity logs', 'Landing zone and organization policy', 'Network segmentation', 'Encryption by default', 'Public exposure'],
      tools: [
        {
          id: 'prowler', name: 'Prowler', pick: 'start', repo: 'prowler-cloud/prowler', license: 'Apache-2.0',
          docs: 'https://docs.prowler.com/', repoPath: 'scanners/prowler',
          role: 'Hundreds of checks for AWS, Azure, GCP, and Kubernetes, mapped to CIS, PCI DSS, ISO 27001, and more.',
          gitlab: 'Upstream GitLab CI cookbook',
          why: 'Answers "are we compliant?" per framework out of the box. The framework mappings are imported in this repository.',
          install: [{ label: 'pip, pipx, or Homebrew', code: 'pip install prowler\n# or\nbrew install prowler' }],
          run: [
            { label: 'AWS against PCI DSS 4.0', code: 'prowler aws --compliance pci_4.0_aws -M csv json-ocsf html -o reports/' },
            { label: 'Other providers', code: 'prowler gcp --project-ids my-project\nprowler azure --az-cli-auth\nprowler kubernetes --kubeconfig-file ~/.kube/config' },
          ],
          ci: `prowler:
  stage: test
  image: python:3.13-slim
  before_script:
    - pip install prowler
  script:
    # use a read-only role; prefer id_tokens + AssumeRoleWithWebIdentity over static keys
    - prowler aws --compliance cis_6.0_aws -M json-ocsf html -o reports/ -z
  artifacts:
    when: always
    paths: [reports/]
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"`,
          results: 'Exit code 3 when checks fail; <code>-z</code> ignores it so the report is always kept. List frameworks with <code>prowler aws --list-compliance</code>.',
        },
        {
          id: 'scoutsuite', name: 'ScoutSuite', repo: 'nccgroup/ScoutSuite', license: 'GPL-2.0',
          docs: 'https://github.com/nccgroup/ScoutSuite/wiki',
          role: 'Multi-cloud audit that builds an offline HTML report of risky configuration.',
          why: 'Built by security consultants for point-in-time reviews: one run collects the configuration, and the report can then be explored offline.',
          install: [{ label: 'pip in a virtual environment', code: 'python3 -m venv venv && . venv/bin/activate\npip install scoutsuite\nscout --help' }],
          run: [{ label: 'Audit an AWS account with a named profile', code: 'scout aws --profile my-audit-profile' }],
          results: 'Opens an HTML report with findings per service. Use a read-only audit role.',
        },
        {
          id: 'cloud-custodian', name: 'Cloud Custodian', repo: 'cloud-custodian/cloud-custodian', license: 'Apache-2.0',
          docs: 'https://cloudcustodian.io/docs/',
          role: 'YAML policies that find and optionally fix non-compliant cloud resources.',
          why: 'Goes beyond reporting: the same policy can tag, notify, stop, or delete offending resources, and it runs on a schedule or on cloud events.',
          install: [{ label: 'pip (add c7n-azure or c7n-gcp for other clouds)', code: 'pip install c7n' }],
          run: [
            { label: 'Example policy (policy.yml)', code: 'policies:\n  - name: ec2-without-owner\n    resource: aws.ec2\n    filters:\n      - "tag:Owner": absent', lang: 'yaml' },
            { label: 'Validate, dry-run, then run', code: 'custodian validate policy.yml\ncustodian run --dryrun -s out policy.yml\ncustodian run -s out policy.yml' },
          ],
          results: 'Matched resources are written under the output directory. Always start with <code>--dryrun</code> before adding actions.',
        },
        {
          id: 'steampipe', name: 'Steampipe and Powerpipe', repo: 'turbot/steampipe', license: 'AGPL-3.0',
          docs: 'https://steampipe.io/docs',
          role: 'Query cloud APIs with SQL and run compliance benchmarks with dashboards.',
          why: 'Ask ad-hoc questions ("which buckets are public?") in SQL, and run ready CIS, PCI, and NIST benchmarks for AWS, Azure, and Google Cloud.',
          install: [{ label: 'Homebrew', code: 'brew install turbot/tap/steampipe turbot/tap/powerpipe\nsteampipe plugin install aws' }],
          run: [{ label: 'Run the AWS CIS benchmark', code: 'powerpipe mod install github.com/turbot/steampipe-mod-aws-compliance\nsteampipe service start\npowerpipe benchmark run aws_compliance.benchmark.cis_v400' }],
          results: 'Benchmarks print pass, fail, and skip per control; <code>powerpipe server</code> opens the dashboards in a browser.',
        },
        {
          id: 'cloudsploit', name: 'CloudSploit', repo: 'aquasecurity/cloudsploit', license: 'GPL-3.0',
          docs: 'https://github.com/aquasecurity/cloudsploit#readme',
          role: 'Configuration checks for AWS, Azure, GCP, and Oracle Cloud with compliance filters.',
          why: 'A lightweight alternative to Prowler that can filter results to HIPAA, PCI, or CIS controls.',
          install: [{ label: 'From source (Node.js)', code: 'git clone https://github.com/aquasecurity/cloudsploit.git\ncd cloudsploit && npm install' }],
          run: [{ label: 'Run PCI checks', code: './index.js --config ./config.js --compliance=pci --json results.json' }],
          results: 'Copy <code>config_example.js</code> to <code>config.js</code> and point it at read-only credentials first.',
        },
      ],
    },
    {
      id: 'cloud-iam', phase: 'run', title: 'Cloud identity and access',
      goal: 'Find over-privileged roles and privilege escalation paths before an attacker uses them.',
      appliesTo: ['Cloud'],
      keywords: 'iam least privilege privilege escalation aws policy roles',
      builtins: [
        { platform: 'AWS', text: 'IAM Access Analyzer finds resources shared outside your account or organization and unused access: <code>aws accessanalyzer create-analyzer --analyzer-name org --type ORGANIZATION</code>.' },
        { platform: 'Azure and Google Cloud', text: 'Microsoft Entra access reviews and Google Cloud IAM Recommender suggest removing unused permissions.' },
      ],
      concepts: ['Least privilege', 'Privilege escalation paths', 'Wildcard actions and resources', 'Unused access', 'Workload identity', 'Break-glass accounts'],
      tools: [
        {
          id: 'pmapper', name: 'PMapper', pick: 'start', repo: 'nccgroup/PMapper', license: 'AGPL-3.0',
          docs: 'https://github.com/nccgroup/PMapper/wiki',
          role: 'Builds a graph of AWS IAM principals and finds who can escalate to admin.',
          why: 'Answers the question that matters in an incident: who can actually reach admin, directly or through role chains.',
          install: [{ label: 'pip', code: 'pip install principalmapper' }],
          run: [
            { label: 'Build the graph for an account', code: 'pmapper --profile my-audit-profile graph create' },
            { label: 'Find privilege escalation paths', code: "pmapper --profile my-audit-profile query 'preset privesc *'\npmapper --profile my-audit-profile query 'who can do iam:CreateUser'" },
          ],
          results: 'Review every non-admin principal that can reach admin. Last updated in 2024, so check results against current AWS behavior.',
        },
        {
          id: 'cloudsplaining', name: 'Cloudsplaining', repo: 'salesforce/cloudsplaining', license: 'BSD-3-Clause',
          docs: 'https://cloudsplaining.readthedocs.io/',
          role: 'Reports AWS IAM policies that allow privilege escalation, data exfiltration, or resource exposure.',
          why: 'Produces a triage-friendly HTML report of risky policies, with an exclusions file to record what you have accepted.',
          install: [{ label: 'pip or Homebrew', code: 'pip install cloudsplaining\n# or\nbrew install cloudsplaining' }],
          run: [{ label: 'Download the account authorization details and scan them', code: 'cloudsplaining download --profile my-audit-profile\ncloudsplaining create-exclusions-file\ncloudsplaining scan --exclusions-file exclusions.yml --input-file default.json --output reports/' }],
          results: 'Start with policies flagged for privilege escalation and data exfiltration.',
        },
      ],
    },
    {
      id: 'cloud-native', phase: 'run', title: 'Native cloud security services',
      goal: 'Turn on the threat detection and posture services your cloud provider already offers.',
      appliesTo: ['Cloud'],
      keywords: 'security hub guardduty security command center defender for cloud aws azure gcp native',
      concepts: ['Threat detection', 'Posture scores', 'Organization-wide enablement', 'Delegated administrator account', 'Finding aggregation'],
      tools: [
        {
          id: 'aws-security-hub', name: 'AWS Security Hub and GuardDuty', pick: 'start', license: 'AWS service (paid)',
          docs: 'https://docs.aws.amazon.com/securityhub/', repoPath: 'reporting/compliance-mapping/prowler',
          role: 'Security Hub aggregates findings and runs standards; GuardDuty detects threats from logs.',
          why: 'Covers what open-source scanners cannot: detection of active threats from CloudTrail, VPC flow, and DNS logs, across every account in the organization.',
          install: [{ label: 'Enable in an account (repeat per region, or use a delegated admin)', code: 'aws securityhub enable-security-hub --enable-default-standards\naws guardduty create-detector --enable' }],
          run: [{ label: 'List high-severity findings', code: "aws securityhub get-findings --filters '{\"SeverityLabel\":[{\"Value\":\"HIGH\",\"Comparison\":\"EQUALS\"}]}'" }],
          results: 'Prowler can send its findings to Security Hub, so open-source and native results appear in one place.',
        },
        {
          id: 'gcp-scc', name: 'Google Security Command Center', license: 'Google Cloud service',
          docs: 'https://cloud.google.com/security-command-center/docs',
          role: 'Posture, misconfiguration, and threat findings for a Google Cloud organization.',
          why: 'Enabled once at the organization level, it covers every project, including ones created later.',
          install: [{ label: 'Activate at the organization level in the Google Cloud console', code: '# Security Command Center > Get started (organization admin required)' }],
          run: [{ label: 'List active findings', code: "gcloud scc findings list organizations/ORGANIZATION_ID --filter='state=\"ACTIVE\"'" }],
        },
        {
          id: 'azure-defender', name: 'Microsoft Defender for Cloud', license: 'Azure service',
          docs: 'https://learn.microsoft.com/azure/defender-for-cloud/',
          role: 'Secure score, recommendations, and workload protection plans for Azure and connected clouds.',
          why: 'The free tier gives posture recommendations and a secure score; paid plans add threat protection per workload type.',
          install: [{ label: 'Enable a Defender plan for a subscription', code: 'az security pricing create -n VirtualMachines --tier standard' }],
          run: [{ label: 'List alerts', code: 'az security alert list -o table' }],
        },
      ],
    },
    {
      id: 'cloud-secrets', phase: 'run', title: 'Cloud secrets and keys',
      goal: 'Store secrets in the cloud provider vault, rotate them, and control keys with KMS.',
      appliesTo: ['Cloud'],
      keywords: 'secrets manager key vault secret manager kms rotation encryption',
      concepts: ['Secret rotation', 'Customer-managed keys (KMS)', 'Key policies', 'Workload identity instead of keys', 'Audit logs for secret access'],
      tools: [
        {
          id: 'aws-secrets-manager', name: 'AWS Secrets Manager', pick: 'start', license: 'AWS service (paid)',
          docs: 'https://docs.aws.amazon.com/secretsmanager/', repoPath: 'skills/secrets-management/aws-secrets-manager',
          role: 'Stores secrets with automatic rotation and IAM-based access.',
          why: 'Rotation is built in for RDS and other databases, and every read is logged in CloudTrail.',
          install: [{ label: 'Create and read a secret', code: 'aws secretsmanager create-secret --name prod/db/password --secret-string "$DB_PASSWORD"\naws secretsmanager get-secret-value --secret-id prod/db/password' }],
          results: 'Grant <code>secretsmanager:GetSecretValue</code> per secret ARN, never on <code>*</code>.',
        },
        {
          id: 'azure-key-vault', name: 'Azure Key Vault', license: 'Azure service',
          docs: 'https://learn.microsoft.com/azure/key-vault/', repoPath: 'skills/secrets-management/azure-keyvault',
          role: 'Secrets, keys, and certificates with Azure RBAC access control.',
          why: 'One vault for secrets, encryption keys, and TLS certificates, with managed identities for applications.',
          install: [{ label: 'Create a vault and a secret', code: 'az keyvault create --name my-vault --resource-group my-rg --enable-rbac-authorization true\naz keyvault secret set --vault-name my-vault --name db-password --value "$DB_PASSWORD"' }],
          results: 'Turn on soft delete and purge protection for production vaults.',
        },
        {
          id: 'gcp-secret-manager', name: 'Google Secret Manager', license: 'Google Cloud service',
          docs: 'https://cloud.google.com/secret-manager/docs', repoPath: 'skills/secrets-management/gcp-secret-manager',
          role: 'Versioned secrets with IAM and audit logging.',
          why: 'Integrates with workload identity on GKE and Cloud Run, so services read secrets without key files.',
          install: [{ label: 'Create a secret and add a version', code: "gcloud secrets create db-password --replication-policy=automatic\nprintf '%s' \"$DB_PASSWORD\" | gcloud secrets versions add db-password --data-file=-" }],
          run: [{ label: 'Read the latest version', code: 'gcloud secrets versions access latest --secret=db-password' }],
        },
      ],
    },
    {
      id: 'runtime', phase: 'run', title: 'Runtime detection',
      goal: 'Detect suspicious behavior in running containers: shells, unexpected network calls, writes to sensitive paths.',
      appliesTo: ['Kubernetes', 'Running apps'],
      keywords: 'runtime detection falco ebpf container escape monitoring',
      concepts: ['Container escape', 'Process monitoring', 'Egress control', 'eBPF', 'Alert routing'],
      tools: [
        {
          id: 'falco', name: 'Falco', pick: 'start', repo: 'falcosecurity/falco', license: 'Apache-2.0',
          docs: 'https://falco.org/docs/', repoPath: 'rules/falco',
          role: 'eBPF-based runtime detection for containers, Kubernetes, and hosts.',
          why: 'The CNCF standard for runtime threat detection. Default rules already catch shells in containers, reads of sensitive files, and privilege escalation.',
          install: [{ label: 'Helm', code: 'helm repo add falcosecurity https://falcosecurity.github.io/charts\nhelm install falco falcosecurity/falco -n falco --create-namespace' }],
          run: [{ label: 'Watch alerts', code: 'kubectl logs -n falco -l app.kubernetes.io/name=falco -f' }],
          results: 'Send alerts to your SIEM or chat with Falcosidekick, and tune noisy rules with exceptions rather than disabling them.',
        },
      ],
    },
    /* ------------------------------------------------------------------ PHASE 5 */
    {
      id: 'vm', phase: 'program', title: 'Vulnerability management and release gates',
      goal: 'Collect findings from every scanner, remove duplicates, decide what blocks a release, and track fixes to closure.',
      appliesTo: ['Team'],
      keywords: 'vulnerability management defectdojo dependency-track triage gates sla kev cvss',
      builtins: [
        { platform: 'GitLab', text: 'the vulnerability report and merge request approval policies, which block merges on new critical findings, need GitLab Ultimate.' },
      ],
      concepts: ['Vulnerability lifecycle', 'CVSS and SSVC', 'KEV catalog', 'Prioritization', 'Deployment and quality gates', 'Risk acceptance with expiry', 'Remediation SLAs', 'Vulnerability disclosure program'],
      tools: [
        {
          id: 'defectdojo', name: 'DefectDojo', pick: 'start', repo: 'DefectDojo/django-DefectDojo', license: 'BSD-3-Clause',
          docs: 'https://docs.defectdojo.com/', repoPath: 'integrations/defectdojo',
          role: 'Imports results from 200+ scanners, deduplicates them, and tracks them per product.',
          why: 'One place for every finding, with parsers for the GitLab report formats and every tool on this page. Reimport closes findings automatically when they disappear.',
          install: [{ label: 'Docker Compose', code: 'git clone https://github.com/DefectDojo/django-DefectDojo\ncd django-DefectDojo && docker compose up -d\ndocker compose logs initializer | grep "Admin password:"' }],
          run: [{ label: 'Import a SARIF report', code: 'curl -X POST "$DD_URL/api/v2/reimport-scan/" \\\n  -H "Authorization: Token $DD_API_KEY" \\\n  -F scan_type="SARIF" -F file=@semgrep.sarif \\\n  -F product_name="my-service" -F engagement_name="CI" \\\n  -F auto_create_context=true' }],
          ci: `defectdojo-upload:
  stage: .post
  image: alpine:3.20
  before_script:
    - apk add --no-cache curl
  script:
    - for f in *.sarif; do
        curl -sf -X POST "$DD_URL/api/v2/reimport-scan/"
          -H "Authorization: Token $DD_API_KEY"
          -F scan_type="SARIF" -F "file=@$f" -F test_title="$f"
          -F product_name="$CI_PROJECT_PATH" -F engagement_name="$CI_DEFAULT_BRANCH"
          -F auto_create_context=true;
      done
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH`,
          results: 'Use <code>reimport-scan</code> for recurring CI scans so fixed findings close automatically. Scan type names come from the parsers, for example "SARIF", "Semgrep JSON Report", "Gitleaks Scan", and "Trivy Scan".',
        },
        {
          id: 'dependency-track', name: 'Dependency-Track', repo: 'DependencyTrack/dependency-track', license: 'Apache-2.0',
          docs: 'https://dependencytrack.github.io/docs/',
          role: 'Continuously re-checks uploaded SBOMs against new vulnerability data.',
          why: 'A scan only tells you about today. Dependency-Track alerts you when a new CVE affects a release you shipped months ago.',
          caution: 'The main branch is v5; v4 reaches end of life in December 2026. Plan new deployments on v5.',
          install: [{ label: 'Deploy with the official quickstart or Helm charts', code: '# https://dependencytrack.github.io/docs/ and github.com/DependencyTrack/helm-charts' }],
          run: [{ label: 'Upload an SBOM', code: 'curl -X POST "$DT_URL/api/v1/bom" -H "X-Api-Key: $DT_API_KEY" \\\n  -F "autoCreate=true" -F "projectName=my-service" \\\n  -F "projectVersion=$CI_COMMIT_REF_NAME" -F "bom=@sbom.cdx.json"' }],
          results: 'The API key needs the BOM_UPLOAD permission, plus project creation permissions for <code>autoCreate</code>.',
        },
        {
          id: 'securecodebox', name: 'secureCodeBox', repo: 'secureCodeBox/secureCodeBox', license: 'Apache-2.0',
          docs: 'https://www.securecodebox.io/docs/getting-started/installation',
          role: 'Runs scanners as Kubernetes jobs on a schedule and ships results to DefectDojo.',
          why: 'For continuous scanning of many targets: nmap, ZAP, nuclei, Trivy, and others run inside the cluster and report automatically.',
          install: [{ label: 'Operator and a scanner (Helm)', code: 'helm --namespace securecodebox-system upgrade --install --create-namespace \\\n  securecodebox-operator oci://ghcr.io/securecodebox/helm/operator\nhelm install nmap oci://ghcr.io/securecodebox/helm/nmap' }],
          run: [{ label: 'Start a scan', code: 'kubectl apply -f nmap-scan.yaml\nkubectl get scans' }],
          results: 'Install the <code>persistence-defectdojo</code> hook to send every result to DefectDojo.',
        },
      ],
    },
    {
      id: 'tm', phase: 'program', title: 'Threat modeling',
      goal: 'Find design flaws before code exists by mapping data flows, trust boundaries, and threats.',
      appliesTo: ['Team'],
      keywords: 'threat modeling stride design dfd',
      concepts: ['STRIDE', 'Data flow diagrams', 'Trust boundaries', 'Attack surface', 'Threat model as code'],
      tools: [
        {
          id: 'threat-dragon', name: 'OWASP Threat Dragon', pick: 'start', repo: 'OWASP/threat-dragon', license: 'Apache-2.0',
          docs: 'https://www.threatdragon.com/docs/', repoPath: 'templates/threat-models',
          role: 'Visual editor for data flow diagrams and STRIDE threats; can store models in GitLab.',
          why: 'The easiest way to start with a team: draw the system, and it suggests threats per element. Models are JSON files you can keep in the repository.',
          install: [{ label: 'Desktop app or container', code: '# desktop installers: github.com/OWASP/threat-dragon/releases\ndocker run -it --rm -p 8080:3000 -v $(pwd)/.env:/app/.env threatdragon/owasp-threat-dragon:stable' }],
          run: [{ label: 'Open the editor', code: 'open http://localhost:8080/' }],
          results: 'Reports are printed or saved as PDF from the model view.',
        },
        {
          id: 'threagile', name: 'Threagile', repo: 'Threagile/threagile', license: 'MIT',
          docs: 'https://threagile.io', repoPath: 'templates/threat-models/threagile',
          role: 'Threat model as YAML with automatic risk rules and reports.',
          why: 'Lives in git and runs in CI, so the threat model is reviewed and updated with the code.',
          install: [{ label: 'Container image', code: 'docker run --rm -it threagile/threagile --help' }],
          run: [
            { label: 'Create an example model', code: 'docker run --rm -it -v "$(pwd)":/app/work threagile/threagile --create-example-model --output /app/work' },
            { label: 'Analyze a model', code: 'docker run --rm -it -v "$(pwd)":/app/work threagile/threagile --model /app/work/threagile.yaml --output /app/work' },
          ],
          results: 'Produces a PDF report, risks as JSON and Excel, and data flow diagrams.',
        },
        {
          id: 'pytm', name: 'pytm', repo: 'OWASP/pytm', license: 'MIT',
          docs: 'https://github.com/OWASP/pytm',
          role: 'Threat model as Python code that generates diagrams and reports.',
          why: 'Suits teams that prefer code to diagrams. Needs Graphviz and PlantUML for diagrams.',
          install: [{ label: 'From source', code: 'git clone https://github.com/OWASP/pytm && cd pytm\npip install -e .' }],
          run: [{ label: 'Generate a diagram and a report', code: './tm.py --dfd | dot -Tpng -o dfd.png\n./tm.py --report docs/basic_template.md > report.md' }],
        },
        {
          id: 'threatcl', name: 'threatcl', repo: 'threatcl/threatcl', license: 'MIT',
          docs: 'https://threatcl.dev/', repoPath: 'templates/threat-models/threatcl',
          role: 'Threat models in HCL with validation, diagrams, and a dashboard.',
          why: 'Feels natural to Terraform users and can validate models against invariants in CI.',
          install: [{ label: 'Homebrew', code: 'brew install threatcl' }],
          run: [{ label: 'Validate models and build a dashboard', code: 'threatcl validate models/*.hcl\nthreatcl dashboard -outdir dashboard models/*.hcl' }],
          results: '<code>threatcl validate -invariants=invariants.hcl</code> exits non-zero on error-severity violations, which makes it usable as a CI gate.',
        },
      ],
    },
    {
      id: 'maturity', phase: 'program', title: 'People, standards, and maturity',
      goal: 'Measure where the program stands, pick the next improvement, and grow security champions in every team.',
      appliesTo: ['Team'],
      keywords: 'maturity samm dsomm asvs masvs standards champions awareness',
      concepts: ['Security champion program', 'Security awareness training', 'Acceptable use policy', 'Maturity levels', 'Security requirements', 'Metrics that matter'],
      tools: [
        {
          id: 'dsomm', name: 'OWASP DSOMM', pick: 'start', repo: 'devsecopsmaturitymodel/DevSecOps-MaturityModel', license: 'GPL-3.0',
          docs: 'https://dsomm.owasp.org/',
          role: 'DevSecOps Maturity Model: activities by dimension and level, with a self-hosted assessment app.',
          why: 'Built for exactly this roadmap: it lists concrete DevSecOps activities per level, so you can mark what you have and plan the next step.',
          install: [{ label: 'Run the assessment app', code: 'docker run --rm -p 8080:8080 wurstbrot/dsomm:latest' }],
          run: [{ label: 'Open it', code: 'open http://localhost:8080/' }],
        },
        {
          id: 'samm', name: 'OWASP SAMM', repo: 'owaspsamm/core', license: 'CC-BY-SA-4.0',
          docs: 'https://owaspsamm.org/',
          role: 'Software Assurance Maturity Model covering governance, design, implementation, verification, and operations.',
          why: 'Broader than DSOMM: use it to report program maturity to management and compare year over year.',
          install: [{ label: 'Use the online assessment or the toolbox spreadsheet', code: '# https://owaspsamm.org/assessment/' }],
        },
        {
          id: 'asvs', name: 'OWASP ASVS', repo: 'OWASP/ASVS', license: 'CC-BY-SA-4.0',
          docs: 'https://owasp.org/www-project-application-security-verification-standard/', repoPath: 'reporting/compliance-mapping/asvs-5.0',
          role: 'Verification requirements for web applications and APIs, in three levels.',
          why: 'Turns "make it secure" into testable requirements for each feature. Version 5.0 is imported in this repository as CSV and JSON.',
        },
        {
          id: 'masvs', name: 'OWASP MASVS', repo: 'OWASP/masvs', license: 'CC-BY-SA-4.0',
          docs: 'https://mas.owasp.org/', repoPath: 'reporting/compliance-mapping/masvs',
          role: 'Security requirements for mobile apps, with the MASTG test guide.',
          why: 'The reference for mobile security reviews. The mobile Semgrep rules in this repository map findings to MASVS controls.',
        },
        {
          id: 'gophish', name: 'GoPhish', repo: 'gophish/gophish', license: 'MIT',
          docs: 'https://getgophish.com/documentation/',
          role: 'Phishing simulation toolkit for security awareness campaigns.',
          why: 'Measures how many people click and how many report, which is the awareness metric that matters. Run it from a dedicated, isolated account and domain.',
          caution: 'Agree on scope, legal approval, and communication with HR before any campaign.',
          install: [{ label: 'Release binary or container', code: '# binaries: github.com/gophish/gophish/releases\ndocker run -it -p 3333:3333 -p 8080:80 gophish/gophish' }],
          run: [{ label: 'Open the admin UI and log in with the password printed in the log', code: 'open https://localhost:3333' }],
          results: 'Track click rate and report rate per campaign; the report rate should rise over time.',
        },
      ],
    },
  ],
};
