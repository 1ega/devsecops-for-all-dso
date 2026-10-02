# Interactive DevSecOps roadmap

[Open the roadmap](https://1ega.github.io/devsecops-for-all-dso/).

The static map covers ten security areas, 29 topics, 95 tools, and all 32 company
baseline controls. Company ownership, identity, SaaS, devices, recovery, external
exposure, logging, incident response and API authorization have dedicated topics.
Topics link repository guides and show acceptance evidence, including topics
that do not require another scanner. Select a
node to read its details beside the map, search for a tool or topic, and mark
tools as adopted. The site starts in dark mode; you can switch to light mode.
Progress and the selected theme are saved in your browser. On wide screens,
the guide panel grows with the viewport and uses larger text. Long commands
wrap visually; the Copy button preserves the original command.

## Files

| File | Purpose |
| :--- | :--- |
| `index.html` | Page shell with generated asset versions |
| `styles.css` | Layout and light/dark themes |
| `app.js` | Map, detail panel, search, and progress |
| `data.js` | Generated areas, topics, manual commands, guides and baseline controls |
| `../tools/roadmap/catalog.json` | Editable topic membership and control/resource mappings |

## Preview locally

From the repository root:

```sh
python3 -m http.server 8000 --directory public
```

Open <http://localhost:8000/>. There are no dependencies or build steps.

## Deployment

The [Pages workflow](../.github/workflows/pages.yml) publishes only `public/`
when site, manual, catalog, baseline or workflow files change on `main`. It can also be run manually
from the Actions tab. In repository **Settings → Pages**, the publishing
source is **GitHub Actions**. Deployment uses the workflow's `GITHUB_TOKEN`;
no personal access token or repository secret is needed.

Edit manuals and the [topic catalog](../tools/roadmap/catalog.json), then run
`python3 tools/roadmap/sync.py`. Run it after editing `app.js` or `styles.css` too;
content hashes in asset URLs prevent old cached cards from surviving an update.
CI rejects missing tools/controls, broken repository
resources and stale generated instructions. See [the maintenance guide](../tools/roadmap/README.md).
Tool IDs also name the linked files in
[`manuals/`](../manuals/). Supported deep links include `#area=code`,
`#area=code&stage=secrets`, and `#tool=gitleaks`.
