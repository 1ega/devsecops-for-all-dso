# MobSF

**Area:** 7. Test what runs → Mobile app builds  
**License:** GPL-3.0  
**Recommended first choice in this topic.**

[GitHub: MobSF/Mobile-Security-Framework-MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF) · [Documentation](https://mobsf.github.io/docs) · [In this repository](https://github.com/1ega/devsecopsforall/tree/main/scanners/mobsf)

## What it is for

Static and dynamic analysis of APK, AAB, and IPA files with a REST API.

The standard open-source mobile analyzer. Run it as a service and let the pipeline upload each release build for analysis.

## Install

**Run the server**

```bash
docker run -it --rm -p 8000:8000 opensecurity/mobile-security-framework-mobsf:latest
```

## Use

**Upload, scan, and fetch the JSON report**

```bash
HASH=$(curl -s -F "file=@app.apk" -H "Authorization: $MOBSF_API_KEY" \
  http://localhost:8000/api/v1/upload | jq -r .hash)
curl -s -X POST -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" http://localhost:8000/api/v1/scan > /dev/null
curl -s -X POST -H "Authorization: $MOBSF_API_KEY" -d "hash=$HASH" http://localhost:8000/api/v1/report_json > mobsf.json
```

## CI example

Pin images and actions to a version or digest before relying on this example.

### GitLab CI

```yaml
mobsf:
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
    paths: [mobsf.json]
```

## Output and triage

The API key comes from the `MOBSF_API_KEY` environment variable of the server. Change the default UI credentials (mobsf/mobsf) on any shared instance.

## Concepts to know

- OWASP MASVS and MASTG
- Decompilation
- Exported components
- Certificate pinning
- Root and jailbreak detection
- Obfuscation

## Related tools

- [apkleaks](apkleaks.md) — Finds URLs, endpoints, and secrets inside an APK.
- [jadx](jadx.md) — Decompiles APK and DEX files to readable Java for manual review.
- [Apktool](apktool.md) — Decodes APK resources and AndroidManifest.xml.
