# Interactive DevSecOps roadmap

[Open the roadmap](https://1ega.github.io/devsecopsforall/).

The static map covers nine security areas, 20 topics, and 91 tools. Select a
node to read its details beside the map, search for a tool or topic, and mark
tools as adopted. Progress and the selected theme are saved in your browser.

## Files

| File | Purpose |
| :--- | :--- |
| `index.html` | Page shell |
| `styles.css` | Layout and light/dark themes |
| `app.js` | Map, detail panel, search, and progress |
| `data.js` | Areas, topics, tools, commands, and repository links |

## Preview locally

From the repository root:

```sh
python3 -m http.server 8000 --directory public
```

Open <http://localhost:8000/>. There are no dependencies or build steps.

## Deployment

The [Pages workflow](../.github/workflows/pages.yml) publishes only `public/`
when site files or the workflow change on `main`. It can also be run manually
from the Actions tab. In repository **Settings → Pages**, the publishing
source is **GitHub Actions**. Deployment uses the workflow's `GITHUB_TOKEN`;
no personal access token or repository secret is needed.

Edit `data.js` to change content. Tool IDs also name the linked files in
[`manuals/`](../manuals/). Supported deep links include `#area=code`,
`#area=code&stage=secrets`, and `#tool=gitleaks`.
