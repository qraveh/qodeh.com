---
title: "SFQ Technology Monitor"
# `summary` (not `description`) on purpose: PaperMod prints .Description as a
# visible sub-title under the H1, which would duplicate the tagline in the body.
# With no .Description set, opengraph.html falls back to .Summary, so this text
# is what ships as <meta name="description"> and <meta property="og:description">.
summary: "An annual, tiered, verification-first assessment of superconducting SFQ digital electronics — technology, ecosystem, and market scenarios to 2035."
date: 2026-08-09
url: "/sfq-monitor/"          # canonical, never changes across editions
aliases: ["/monitor/"]        # optional short alias (publishing decisions)
layout: "single"
author: "Raveh Neeman"
hideMeta: true                # a living pointer page, not a dated post
ShowBreadCrumbs: false
ShowPostNavLinks: false

# Google Scholar / schema.org metadata, rendered into <head> by
# layouts/partials/extend_head.html. The {{...}} placeholders are filled on
# release day by the HANDOFF release ticket, after editor-in-chief sign-off —
# `grep -r "{{" content/sfq-monitor/` finds every one of them.
monitor:
  citation_title: "SFQ Technology Monitor 2026"
  citation_author: "Neeman, Raveh"
  citation_publication_date: "2026/08/09"
  # v1.0 ships the deck alone, so this points at the deck. Flip it back to the
  # article rendering at v1.1 — Scholar indexes article-format PDFs reliably, decks poorly.
  citation_pdf_url: "https://qodeh.com/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf"
  citation_doi: "10.5281/zenodo.21860768"
  version: "1.0"
  date_published_iso: "2026-08-09"
  license: "https://creativecommons.org/licenses/by/4.0/"
  version_doi: "10.5281/zenodo.21860768"
---

**SFQ Technology Monitor** — an annual, tiered, verification-first assessment of superconducting single-flux-quantum digital electronics: technology state, ecosystem, and market scenarios.

## Current edition

<div class="monitor-card">

**SFQ Technology Monitor 2026 · v1.0** · data cut-off 9 August 2026 · published 9 August 2026

Download: **[Deck (PDF)](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf)**

<!-- v1.0 ships the deck alone: the article rendering was not release-ready at freeze.
     When it ships, restore on this line:
       · **[Report (PDF)](/sfq-monitor/files/SFQ-Technology-Monitor-2026-report_v1.1.pdf)**
     and restore the two-rendering sentence:
       *The deck is the Monitor's primary form; the report is the same edition-version
        rendered as an article. Same claims, same numbers, same tiers.*
     Also flip `citation_pdf_url` in the front matter back to the report — Scholar
     indexes article-format PDFs reliably and decks poorly. -->

*The deck is the Monitor's primary form.*

</div>

## Cite as

> Neeman, R., "SFQ Technology Monitor 2026," v1.0, Qodeh, 2026. doi:10.5281/zenodo.21860768 (all versions: 10.5281/zenodo.21860767).

DOI resolves to the archival record (Zenodo); this page is the living pointer.

## Version log

| Date | Version | What changed |
|---|---|---|
| 9 August 2026 | v1.0 | Initial public release. |

*Corrections policy as practiced: fixes of what was wrong as of the data cut-off ship as v1.x with a log line here; post-cut-off developments belong to the next edition, not to this one. Every published file is immutable; superseded versions remain in the archive below.*

## Archive

<!-- v1.0 only at launch; each later version adds one row: version · date · deck PDF · its DOI.
     The Report column is omitted while no report has shipped — an empty column reads as a
     missing file rather than a rendering that does not exist yet. Restore it at v1.1. -->

| Version | Date | Deck | DOI |
|---|---|---|---|
| v1.0 | 9 August 2026 | [PDF](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf) | 10.5281/zenodo.21860768 |

## Corrections

Factual corrections are welcome: **[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com?subject=SFQ%20Monitor%20correction)** (subject: "SFQ Monitor correction"). Underlying Qodeh research analyses are available on request.

<!--
  Phase 3 (arXiv) only — do NOT render an empty promise before the ID exists.
  When arXiv publishes, add the preprint line here with {{ARXIV_ID}} filled in.
-->
