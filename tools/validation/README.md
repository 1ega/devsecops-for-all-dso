# Repository validation

```bash
python3 -m pip install -r tools/validation/requirements.txt
python3 tools/validation/check_repo.py
python3 tools/roadmap/sync.py --check
python3 -m unittest discover -s tools/roadmap/tests -v
python3 -m yamllint .
python3 -m unittest discover -s tools/dso/tests -v
python3 -m pip install --require-hashes -r mcp/dso/requirements.lock
python3 -m unittest discover -s mcp/dso/tests -v
bash rules/falco/validate.sh
```

The checker validates owned YAML/JSON syntax (including YAML fences in manuals),
duplicate YAML keys, accidental null/mapping commands in GitLab examples, relative
Markdown links, and Falco rule/catalog/scenario consistency. Imported directories
with `SOURCE.md` retain their upstream schemas and are excluded. It does not
evaluate scanner rules or verify live configurations. Native Falco compilation
runs separately, and [runtime smoke testing](../../rules/falco/tests/README.md)
requires Linux Docker. Python tools are pinned in `requirements.txt`.

[`.yamllint.yml`](../../.yamllint.yml) lints the YAML this repository authors,
including workflows and copyable CI templates. Imported packs and upstream-style
rule files are listed in its `ignore` block; add new imports there too.
