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

## Contact

[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com)
