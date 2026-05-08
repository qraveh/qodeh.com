---
title: "I Shipped a Production Go Project Without Knowing Go"
subtitle: "A Case Study in AI-Assisted Software Development"
date: 2026-05-07
summary: "A case study of building SelectiveMirror — a real-sized Windows Go service with installer, telemetry, SQL backend, and ISO-aligned engineering — in about six weeks, while contributing zero lines of Go. What changed: the human role."
tags: ["selective-mirror", "ai-assisted-development", "software-engineering", "case-study", "go"]
author: "Raveh Neeman"
showToc: true
TocOpen: false
---

*A Case Study in AI-Assisted Software Development*

> **TL;DR.** Selective mirroring with improved `.gitignore`-like syntax to any cloud via rclone (70+ platforms). Built solo in six weeks: production-grade, ~22K lines of Go, AI-only. A 10x acceleration compared with pre-AI software product development. The human role: Product Manager, Architect, V&V Manager, … — not coder. Asking the right questions is key.

SelectiveMirror is written in Go.

I cannot write "Hello, World!" in Go.

I did not learn Go for this project. I did not open Go files to inspect syntax. I did not debug compiler errors. My coding contribution was zero percent.

The opposite of "I do not code" was a different kind of active work: product definition, project control, architectural judgment, lifecycle thinking, verification pressure, and constant questioning of what would happen in the hands of a real user.

My role was the role software teams usually split across several people: Product Manager, Project Manager, Architect, and sometimes Verification Manager. I defined the product, introduced an SQL state database for correct synchronization in a multi-stage, multi-agent environment, organized multilayered verification and system validation, protected the lifecycle, shaped the architecture, set release expectations, demanded tests, rejected weak verification, and kept asking, relentlessly, what would happen to a real user after installation, upgrade, crash, uninstallation, misconfiguration, or a support request.

That combination is the key.

> The person who gets the most from coding AI is not merely "the best coder." It is the person who combines the virtues of product management, project management, and architecture.

## Product Thinking

Product management asks: what is this thing for?

SelectiveMirror started because I needed shared storage for AI orchestration, but the product could not just be "sync my files." It needed a clear user promise:

> Selective, real-time, explainable mirroring from local project folders to any `rclone` backend.

That meant saying no to whole categories of complexity. It was one-way mirroring, not bidirectional collaboration. It was CLI-first, not GUI-first. It used `.gitignore` semantics instead of inventing a new filter language. It used `rclone` instead of writing cloud integrations.

Those were product decisions.

They gave the AI a stable target.

## Project Thinking

Project management asks: where are we in the lifecycle?

This mattered constantly. A working binary was not enough. I had to think about first use, personal use, public release, installation, updates, support, bug reports, telemetry, security, and eventual maturity.

At the end of the first day, I could use mirroring myself.

At the end of the first week, I could release the product to others, with a fair number of known tradeoffs.

The remaining five weeks were mostly about lifecycle issues I did not fully know at the beginning: MSI behavior, Windows service permissions, scheduled tasks, telemetry, SQL backend design, security audit findings, release gates, regression tests, documentation consistency, and how a user reports a bug without leaking private paths.

> AI made implementation fast. It did not magically make the product manager know every production concern on day one.

That was the important human learning curve.

## Architecture Thinking

Architecture asks: what foundations make the system durable?

The key architectural move was to build on solid ground. `.gitignore` for filter semantics. `rclone` for transport. Go for a single binary. SQLite for local state. SQL-backed telemetry for product feedback. Explicit delete policies. A CLI that exposes diagnostics instead of hiding them.

At v1.0.0, SelectiveMirror is a real-sized project:

| Metric | Current scale |
|---|---|
| Git commits | 282 |
| Tagged releases | 8 tags, v0.4.0 through v1.0.0 — full list at [GitHub Releases](https://github.com/qraveh/SelectiveMirror/releases) |
| Total tracked lines | 81,535 |
| Go source lines | 54,595 total Go lines (22,766 production + 31,829 test) |
| CLI implementation | 8,916 production Go lines in `cmd/smirror` |
| Internal packages | 29,824 Go lines in `internal/` |
| Documentation | 10,728 Markdown lines (`docs/` plus root Markdown) |
| Telemetry SQL/backend source/docs | 2,513 lines (excluding generated package-lock) |
| Installer code/config | 1,177 lines |
| BugTracker records | 216 |
| Go test/fuzz functions | 1,060 (1,055 Test + 5 Fuzz) |
| Regression scope | 1,060 Go test/fuzz functions plus system/integration validation; telemetry CLAIMS-MAP 25/28 GREEN |

It includes a Windows service mode, per-user Scheduled Task mode, MSI installer, self-update flow, local SQLite state database, telemetry backend, Cloudflare Worker proxy, release automation, security hardening, SRS, V&V planning, and structured bug reporting.

This was a standards-based project aligned with ISO engineering practices, though not externally certified to ISO standards. Claude audited the project against ISO-aligned criteria and reported strong alignment with Requirements Engineering ISO 29148:2018, Product Quality Model ISO 25010:2023, Quality Measurement ISO 25023:2016, and Software Testing ISO 29119:2023.

At the last round of ISO compliance audit, Claude BMAD arrived. The AI work became explicitly multirole.

- **PM John** audited requirements engineering.
- **Architect Winston** owned the quality model.
- **Tech-writer Paige** took on the documentation, of course.
- **Developer Amelia** focused on the test-process gaps that require code/CI changes.
- **The Edge-case Hunter** and **the Adversarial Reviewer** challenged and validated the audit before sign-off.
- **Claude GUI assistant** orchestrated them as the lead, wrote the master doc, and delegated parallel reviews.

AI can write the code, but it does not automatically choose the right product boundary or operational philosophy. That remains human work.

## Verification Thinking

Verification asks: why should I believe this works?

This became one of the most important parts of the project. Claude helped build and fix the product. By v1.0.0, the BugTracker held 216 records. Yet at one point, after a large Claude-led bug-fixing cycle, a Claude-led system-level verification pass found zero new bugs.

I did not accept that.

Zero bugs in a young filesystem/cloud/Windows service product is not a clean bill of health. It is suspicious.

So I brought in Codex as an independent reviewer. Codex learned the product from documentation and found dozens of real issues; by v1.0.0, Codex-linked reviews accounted for 75 BugTracker records.

> Cross-AI verification matters. Different AIs have different blind spots. Claude was strong as builder and fixer. Codex was strong as adversarial investigator. Diversity still matters, even when the workers are artificial.

This was not cosmetic review. It changed the product. It found real issues in exit codes, failure masking, filter behavior, status reporting, batch sync paths, sanitization, and operational diagnostics.

## The 10x Acceleration

The acceleration claim is not based on vibes.

A conservative human estimate for the current SelectiveMirror scope is roughly one year for a strong solo engineer, and several months for a small well-coordinated team. That includes product design, implementation, testing, installer work, Windows service behavior, security hardening, telemetry, SQL backend, documentation, regression infrastructure, and release engineering.

With coding AI, I reached this level in about six weeks.

That is the rounded 10x claim.

Actually, that may be too modest.

This was the first project. The learning curve was included in the clock, not excluded from it: how to steer AI engineers, how to hold a product boundary, how to force verification, how to think about installers, support, telemetry, privacy, audits, and failure modes.

The next product does not start from zero. The AI improve. I improve. A human who has already released one AI-built product brings release instincts to the next one. From that perspective, 10x is a conservative understatement.

Some milestones were even more compressed:

![SelectiveMirror milestones — AI-assisted actual vs. human-only estimates](/milestones.png)

| Milestone | AI-assisted actual | Human estimate without AI |
|---|---|---|
| Personally usable mirroring | 1 day | 2–4 weeks |
| Public release with tradeoffs | 1 week | 2–3 months |
| v1.0.0 stable release | ~6 weeks | ~12 months |
| 1,060 Go test/fuzz functions and 216 bug records | Concurrent | additional months |

For me personally, the multiplier is even larger, because without AI I would first need to learn Go or hire implementation. The project would not merely be slower. It probably would not exist in this form.

## The New Role

This is why the "AI replaces developers" framing is too crude.

Coding AI changes *who* can lead software creation. The limiting factor becomes less "can you personally write this language?" and more:

- Can you define the product clearly?
- Can you manage scope and lifecycle?
- Can you make architectural decisions?
- Can you recognize missing production concerns?
- Can you design verification pressure?
- Can you distrust suspiciously clean results?
- Can you coordinate multiple AI agents with different strengths?

In SelectiveMirror, I was not the Go developer.

I was the person holding product intent, project discipline, architectural coherence, and verification pressure.

That is the profile that works best with coding AI.

Not coder alone.

Not architect alone.

An experienced human who knows which questions to ask, when to distrust easy answers, and how to keep asking until the system is production-ready.

---

## Project links

- **Repository:** [github.com/qraveh/SelectiveMirror](https://github.com/qraveh/SelectiveMirror)
- **Releases:** [github.com/qraveh/SelectiveMirror/releases](https://github.com/qraveh/SelectiveMirror/releases/)
- **v1.0.0 release notes:** [v1.0.0 tag](https://github.com/qraveh/SelectiveMirror/releases/tag/v1.0.0)
- **MSI installer (Windows):** [SelectiveMirror.msi](https://github.com/qraveh/SelectiveMirror/releases/download/v1.0.0/SelectiveMirror.msi)
