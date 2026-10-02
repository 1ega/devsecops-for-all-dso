# apkleaks

**Area:** 7. Test what runs → Mobile app builds  
**License:** Apache-2.0

[GitHub: dwisiswant0/apkleaks](https://github.com/dwisiswant0/apkleaks) · [Documentation](https://github.com/dwisiswant0/apkleaks) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/scanners/apkleaks)

## What it is for

Finds URLs, endpoints, and secrets inside an APK.

A quick check that release builds do not carry API keys or internal URLs. Its patterns are imported in this repository.

## Install

**pip**

```bash
pip3 install apkleaks
```

## Use

**Scan an APK to JSON**

```bash
apkleaks -f app-release.apk -o apkleaks.json --json
```

## Output and triage

Needs jadx and offers to download it. There is no findings-based exit code, so review the report or gate with jq.

## Concepts to know

- OWASP MASVS and MASTG
- Decompilation
- Exported components
- Certificate pinning
- Root and jailbreak detection
- Obfuscation

## Related tools

- [MobSF](mobsf.md) — Static and dynamic analysis of APK, AAB, and IPA files with a REST API.
- [jadx](jadx.md) — Decompiles APK and DEX files to readable Java for manual review.
- [Apktool](apktool.md) — Decodes APK resources and AndroidManifest.xml.
