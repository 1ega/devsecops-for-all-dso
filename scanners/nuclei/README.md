# nuclei

Custom [nuclei](https://github.com/projectdiscovery/nuclei) templates for API-specific issues — IDOR patterns, sensitive data in responses, exposed internal endpoints — and a curated tag selection from [nuclei-templates](https://github.com/projectdiscovery/nuclei-templates).

Every template needs a safe, local target that demonstrates a match and a non-match.

Imported: [fuzzing-templates](../../rules/nuclei/fuzzing-templates/SOURCE.md) — 21 archived nuclei fuzzing templates (MIT) for query parameters and request bodies. The full [nuclei-templates](https://github.com/projectdiscovery/nuclei-templates) library is too large and changes daily; use it from upstream with `nuclei -update-templates`.

**Status:** Fuzzing templates imported; custom templates are not published yet.
