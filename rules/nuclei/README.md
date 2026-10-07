# nuclei templates

| Package | Use |
| :--- | :--- |
| [fuzzing-templates](fuzzing-templates/SOURCE.md) | 21 archived nuclei fuzzing templates (MIT) for query parameters and request bodies: command injection, CRLF, client- and server-side template injection, local and remote file inclusion, open redirect, SQL injection, SSRF, XSS and XXE. |

Upstream archived this repository and moved the templates into
[nuclei-templates](https://github.com/projectdiscovery/nuclei-templates) under `dast/`.
Prefer that maintained copy for new work; this one stays as a small, reviewed set.

## Run

Fuzzing sends attack payloads. Run it only against a system you are authorized to
test, preferably staging, and never against production without an agreement.
Install [nuclei](../../manuals/nuclei.md) and run from the repository root:

```bash
nuclei -dast -t rules/nuclei/fuzzing-templates \
  -u 'https://staging.example.com/search?q=test' \
  -rate-limit 10 -sarif-export /private/reports/nuclei-fuzzing.sarif
```

Templates fuzz the parameters of the URLs you give them, so pass URLs that carry
parameters, or a list of them with `-l urls.txt`. See the [nuclei scanner notes](../../scanners/nuclei/README.md).
