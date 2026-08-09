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
  citation_publication_date: "{{RELEASE_DATE_YYYY/MM/DD}}"
  citation_pdf_url: "https://qodeh.com/sfq-monitor/files/SFQ-Technology-Monitor-2026-report_v1.0.pdf"
  citation_doi: "{{VERSION_DOI}}"
  version: "1.0"
  date_published_iso: "{{RELEASE_DATE_ISO}}"
  license: "https://creativecommons.org/licenses/by/4.0/"
  version_doi: "{{VERSION_DOI}}"
---

**SFQ Technology Monitor** — an annual, tiered, verification-first assessment of superconducting single-flux-quantum digital electronics: technology state, ecosystem, and market scenarios.

## Current edition

<div class="monitor-card">

**SFQ Technology Monitor 2026 · v1.0** · data cut-off {{CUTOFF_DATE}} · published {{RELEASE_DATE}}

Download: **[Deck (PDF)](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf)** · **[Report (PDF)](/sfq-monitor/files/SFQ-Technology-Monitor-2026-report_v1.0.pdf)**

*The deck is the Monitor's primary form; the report is the same edition-version rendered as an article. Same claims, same numbers, same tiers.*

</div>

## Cite as

> Neeman, R., "SFQ Technology Monitor 2026," v1.0, Qodeh, {{RELEASE_YEAR}}. doi:{{VERSION_DOI}} (all versions: {{CONCEPT_DOI}}).

DOI resolves to the archival record (Zenodo); this page is the living pointer.

## Version log

| Date | Version | What changed |
|---|---|---|
| {{RELEASE_DATE}} | v1.0 | Initial public release. |

*Corrections policy as practiced: fixes of what was wrong as of the data cut-off ship as v1.x with a log line here; post-cut-off developments belong to the next edition, not to this one. Every published file is immutable; superseded versions remain in the archive below.*

## Archive

<!-- v1.0 only at launch; each later version adds one row: version · date · deck PDF · report PDF · its DOI. -->

| Version | Date | Deck | Report | DOI |
|---|---|---|---|---|
| v1.0 | {{RELEASE_DATE}} | [PDF](/sfq-monitor/files/SFQ-Technology-Monitor-2026_v1.0.pdf) | [PDF](/sfq-monitor/files/SFQ-Technology-Monitor-2026-report_v1.0.pdf) | {{VERSION_DOI}} |

## Corrections

Factual corrections are welcome: **[raveh.neeman@qodeh.com](mailto:raveh.neeman@qodeh.com?subject=SFQ%20Monitor%20correction)** (subject: "SFQ Monitor correction"). Underlying Qodeh research analyses are available on request.

<!--
  Phase 3 (arXiv) only — do NOT render an empty promise before the ID exists.
  When arXiv publishes, add the preprint line here with {{ARXIV_ID}} filled in.
-->
