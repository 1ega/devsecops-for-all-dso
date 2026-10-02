# jadx

**Area:** 7. Test what runs → Mobile app builds  
**License:** Apache-2.0

[GitHub: skylot/jadx](https://github.com/skylot/jadx) · [Documentation](https://github.com/skylot/jadx/wiki)

## What it is for

Decompiles APK and DEX files to readable Java for manual review.

Lets you review what is really inside a release build and run Semgrep rules on the decompiled code.

## Install

**Homebrew**

```bash
brew install jadx
```

## Use

**Decompile an APK**

```bash
jadx -d out app.apk
```

## Concepts to know

- OWASP MASVS and MASTG
- Decompilation
- Exported components
- Certificate pinning
- Root and jailbreak detection
- Obfuscation

## Related tools

- [MobSF](mobsf.md) — Static and dynamic analysis of APK, AAB, and IPA files with a REST API.
- [apkleaks](apkleaks.md) — Finds URLs, endpoints, and secrets inside an APK.
- [Apktool](apktool.md) — Decodes APK resources and AndroidManifest.xml.
