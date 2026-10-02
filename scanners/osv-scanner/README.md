# osv-scanner

Dependency scanning against the [OSV](https://osv.dev/) database for backend and mobile lockfiles: Gradle, `Podfile.lock`, `Package.resolved`, `pubspec.lock`, `package-lock.json`, and `yarn.lock`.

Planned contents: a scanner config, an ignore file where every entry has a reason and an expiry date, and a denylist of banned packages (trackers, abandoned or known-bad versions).

Research candidates: [google/osv-scanner](https://github.com/google/osv-scanner), [anchore/grype](https://github.com/anchore/grype), [jeremylong/DependencyCheck](https://github.com/jeremylong/DependencyCheck). Check CocoaPods and Swift Package Manager support before choosing. Related skill: [dependency-scanning](../../skills/supply-chain/dependency-scanning/SKILL.md).

**Status:** Structure only; no configuration is published yet.
