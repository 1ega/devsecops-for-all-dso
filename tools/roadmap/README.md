# Keep the interactive roadmap in sync

The website's instructions come from `manuals/*.md`. Topic membership, concepts,
repository guides, acceptance steps and baseline mappings live in
`catalog.json`. Keep tool IDs stable: they are manual filenames, deep links and
browser adoption keys. `public/data.js` is generated and committed so the site
still needs no runtime dependencies or build service.

```bash
python3 tools/roadmap/sync.py
python3 tools/roadmap/sync.py --check
python3 -m unittest discover -s tools/roadmap/tests -v
node --check public/data.js
node --check public/app.js
```

The checker rejects duplicate/orphan topics, missing manuals or repository
resources, duplicated instructions in the catalog, and baseline controls without
a topic. `--check` also fails if a manual changed without regenerating the site.
GitHub kit and Pages workflows run this check. Add a new manual's catalog entry
and baseline mapping before publishing its generated data.

The renderer escapes manual text and permits only HTTP(S) or relative Markdown
links. It displays repository validation limits and acceptance steps separately
from a visitor's browser-local adoption marker. The marker is not evidence that
a control works. Linked guides and imported packs still require environment
acceptance testing.
