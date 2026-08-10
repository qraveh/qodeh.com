---
title: "SFQ Technology Monitor 2026"
# `summary` (not `description`) on purpose: PaperMod prints .Description as a
# visible sub-title under the H1, which would duplicate the tagline in the body.
# With no .Description set, opengraph.html falls back to .Summary, so this text
# is what ships as <meta name="description"> and <meta property="og:description">.
summary: "An annual, tiered assessment of superconducting SFQ digital electronics — technology, ecosystem, and market scenarios to 2035."
date: 2026-08-09
url: "/sfq-monitor/"          # canonical, never changes across editions
aliases: ["/monitor/"]        # optional short alias (publishing decisions)
layout: "single"
author: "Raveh Neeman"
hideMeta: true                # a living pointer page, not a dated post
ShowBreadCrumbs: false
ShowPostNavLinks: false

# Google Scholar / schema.org metadata, rendered into <head> by
# layouts/partials/extend_head.html. Filled at release; `grep -r "{{"
# content/sfq-monitor/` finds anything still unfilled.
monitor:
  citation_title: "SFQ Technology Monitor 2026"
  citation_author: "Neeman, Raveh"
  citation_publication_date: "2026/08/09"
  # v1.0 ships the presentation alone, so this points at it. Flip it back to the
  # article rendering at v1.1 — Scholar indexes article-format PDFs reliably.
  citation_pdf_url: "https://qodeh.com/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf"
  # Concept DOI on purpose: it always resolves to the newest version, which is
  # what this permanent landing page points at. Per-version DOIs live in the
  # Archive table below, where identifying a specific version is the point.
  citation_doi: "10.5281/zenodo.21860767"
  version: "1.0"
  date_published_iso: "2026-08-09"
  license: "https://creativecommons.org/licenses/by/4.0/"
  # feeds JSON-LD sameAs; concept DOI, matching citation_doi above
  version_doi: "10.5281/zenodo.21860767"
---

**SFQ Technology Monitor** — an annual, tiered assessment of superconducting single-flux-quantum digital electronics: technology state, ecosystem, and market scenarios.

## Current edition

<div class="monitor-card">

**[SFQ Technology Monitor 2026](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf)** · v1.0 · published 9 August 2026

<!-- v1.0 ships the presentation alone: the article rendering was not release-ready
     at freeze. When it ships, add it to the line above:
       · **[Article rendering](/sfq-monitor/files/SFQ-Technology-Monitor-2026-report_v1.1.pdf)**
     and flip `citation_pdf_url` in the front matter back to it — Scholar indexes
     article-format PDFs reliably. -->

</div>

## Cite as

> Neeman, R., "SFQ Technology Monitor 2026," v1.0, Qodeh, 2026. doi:[10.5281/zenodo.21860767](https://doi.org/10.5281/zenodo.21860767)

DOI resolves to the archival record (Zenodo) and always to its current version; this page is the living pointer.

## Version log

| Date | Version | What changed |
|---|---|---|
| 9 August 2026 | v1.0 | Initial public release. |

## Archive

<!-- v1.0 only at launch; each later version adds one row: version · date · PDF · its DOI.
     A second file column returns at v1.1 when the article rendering ships — an empty
     column reads as a missing file rather than one that does not exist yet. -->

| Version | Date | PDF | DOI |
|---|---|---|---|
| v1.0 | 9 August 2026 | [Download](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf) | [10.5281/zenodo.21860768](https://doi.org/10.5281/zenodo.21860768) |

## Corrections

Factual corrections are welcome: **[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com?subject=SFQ%20Monitor%20correction)**

<!--
  Phase 3 (arXiv) only — do NOT render an empty promise before the ID exists.
  When arXiv publishes, add the preprint line here with {{ARXIV_ID}} filled in.
-->
