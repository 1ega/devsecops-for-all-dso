# Repository validation

```bash
python3 -m pip install -r tools/validation/requirements.txt
python3 tools/validation/check_repo.py
python3 -m unittest discover -s tools/dso/tests -v
bash rules/falco/validate.sh
```

The checker validates owned YAML/JSON syntax (including YAML fences in manuals),
duplicate YAML keys, accidental null/mapping commands in GitLab examples, relative
Markdown links, and Falco rule/catalog/scenario consistency. Imported directories
with `SOURCE.md` retain their upstream schemas and are excluded. It does not
evaluate scanner rules or verify live configurations. Native Falco compilation
runs separately, and [runtime smoke testing](../../rules/falco/tests/README.md)
requires Linux Docker. Python tools are pinned in `requirements.txt`.
