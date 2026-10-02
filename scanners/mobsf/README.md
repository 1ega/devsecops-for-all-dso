# MobSF

Analysis of built mobile artifacts (APK, AAB, IPA) to find what source rules cannot see: `debuggable` builds, embedded secrets, native libraries, exported components, permissions, and missing obfuscation. Complements the [mobile Semgrep rules](../../semgrep-rules/mobile_custom/README.md).

Research candidates:

| Tool | Project | Notes |
| :--- | :--- | :--- |
| MobSF | [MobSF/Mobile-Security-Framework-MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) | Static and dynamic analysis, REST API |
| apkleaks | [dwisiswant0/apkleaks](https://github.com/dwisiswant0/apkleaks) | Secrets and URLs in APKs |
| Quark Engine | [quark-engine/quark-engine](https://github.com/quark-engine/quark-engine) | Android behavior analysis |
| jadx | [skylot/jadx](https://github.com/skylot/jadx) | Decompilation for manual review |

Imported: [../apkleaks](../apkleaks/SOURCE.md) — the regular expressions apkleaks applies to decompiled APKs (Apache-2.0). Related skill: [firebase-apk-scanner](../../skills/trailofbits/firebase-apk-scanner/README.md) for Firebase misconfigurations in APKs.

Open question: a self-hosted MobSF instance with its API, or CLI tools only inside CI.

**Status:** Structure only; no configuration is published yet.
