# The site contract

The rules a change to qodeh.com must keep, checked by `scripts/check_site.py` against a built site. Only the local
Claude Code session changes the site; cloud sessions send structured tickets (redesign brief, 2026-10-11).

| File | What it fixes |
|---|---|
| `frozen-urls.txt` | Paths that must keep resolving forever (cited by Zenodo, colophons, outreach letters, the Atlas build). |
| `citation-pages.txt` | Pages that must carry Google Scholar `citation_*` meta and a schema.org graph. |
| `budget.json` | Per-page weight budget and the image-size ceiling. |

Run after a build:

```bash
hugo --destination public
python scripts/check_site.py public              # the Hugo site alone (Atlas paths skipped)
python scripts/check_site.py public --with-atlas # after the deploy assembled the Atlas into public/
```

Exit code 0 means every rule holds; 1 means at least one failure (the report names each). Warnings never fail the run.
