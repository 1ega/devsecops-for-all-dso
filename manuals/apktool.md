# Apktool

**Area:** 7. Test what runs → Mobile app builds  
**License:** Apache-2.0

[GitHub: iBotPeaches/Apktool](https://github.com/iBotPeaches/Apktool) · [Documentation](https://apktool.org)

## What it is for

Decodes APK resources and AndroidManifest.xml.

Needed to inspect the final merged manifest: exported components, debuggable and backup flags, network security config.

## Install

**Download from the project site**

```bash
# see https://apktool.org for the wrapper script and jar
```

## Use

**Decode an APK**

```bash
apktool d app.apk -o app_out
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
- [jadx](jadx.md) — Decompiles APK and DEX files to readable Java for manual review.
