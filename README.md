# qodeh.com

Personal site of [Raveh Neeman](https://www.linkedin.com/in/ravehneeman/),
quantum computing researcher.

Live at <https://qodeh.com>.

## Stack

- [Hugo](https://gohugo.io/) — static site generator (**Extended edition, 0.160.1**;
  any Extended release from 0.146+ should work — the build uses Goldmark with
  `unsafe: true`, image processing, and the modern `build:` front-matter key)
- [PaperMod](https://github.com/adityatelange/hugo-PaperMod) — theme,
  vendored at `themes/PaperMod/` under its own MIT license
- GitHub Pages — hosting

## Build locally

Requires Hugo Extended ≥ 0.146 (`hugo version` should print `+extended`).

```powershell
git clone https://github.com/qraveh/qodeh.com.git
cd qodeh.com

# Run dev server (auto-reload)
hugo server
```

Open <http://localhost:1313/>.

## Published files (`/sfq-monitor/files/`)

Citable publications are served as static files under
`static/sfq-monitor/files/`, and the rules are deliberate:

- **One immutable file per version.** A published file is never edited in
  place and its name is never reused. A fix ships as a new version
  (`…_v1.1.pdf`) plus a row in the version log on the landing page.
- **No `latest.pdf`.** <https://qodeh.com/sfq-monitor/> is the only "latest"
  pointer. A mutable filename would break every citation that used it.
- **Naming:** `SFQ-Technology-Monitor-<edition>_<version>.pdf` for the deck and
  `SFQ-Technology-Monitor-<edition>-report_<version>.pdf` for the article
  rendering of the same edition-version.
- The canonical URL `/sfq-monitor/` never changes across editions; the
  archival record and the citable DOI live on Zenodo.

The landing page itself is `content/sfq-monitor/index.md`. Its `monitor:`
front-matter block feeds the Google Scholar `citation_*` tags and the
schema.org `Report` graph via `layouts/partials/extend_head.html` — so a
release only ever edits content, never templates.

## Site search

One search over the site's pages and the Quantum Technology Atlas's records
(technologies, machines, organisations, architectures, glossary), modelled on
the Atlas's own Find. It opens from any page with `/` or Ctrl+K (⌘K) or the
menu's Search, and the `/search/` page keeps the query in its address
(`?q=…&cs=1&w=1&l=ru`). The query is a regular expression; options are case,
whole word and the Atlas's language. Each hit links to its page with a text
fragment that scrolls to it, and glossary hits open the Atlas with its Find
already running.

- `assets/js/qsearch.js` (UI) and `assets/js/qsearch/core.js` (matching,
  ranking, snippets): bundled by Hugo into one deferred script on every page,
  about 5 KB compressed.
- `scripts/build_search_index.py` writes `public/search/*.json` from the built
  output, in the deploy after the Atlas is assembled.
  - `site.json` and `atlas-<lang>.json` hold the pages, the record titles and
    descriptions, and the glossary. They are about 45 KB compressed, fetched
    at idle unless the reader saves data.
  - `atlas-<lang>-text.json` holds the records' full text (about 1 MB in
    English), fetched when the search opens.
  - `/search/*` is served `no-cache`.
- Tests: `python scripts/test_build_search_index.py`,
  `node --test tests/qsearch_core.test.mjs`. Both run in the deploy before the
  index is built.
- Locally: build Hugo, copy a built Atlas `dist/` to
  `<out>/publications/quantum-technology-atlas/`, then run
  `python scripts/build_search_index.py <out> --glossary <qt-map>/data`.
- Without JavaScript, `/search/` lists every page and the Atlas's record lists.

## Contact

[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com)
