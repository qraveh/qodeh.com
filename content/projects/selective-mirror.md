---
title: "SelectiveMirror"
date: 2026-03-29
lastmod: 2026-05-07
summary: "A Windows-first selective file-mirroring service with rclone backend support. Near-real-time, filter-aware, bandwidth-efficient. Released v1.0.0."
tags: ["go", "windows", "rclone", "file-sync"]
weight: 1
---

A Windows-first service that watches local directories for file changes and mirrors them to any [rclone](https://rclone.org/)-supported backend — Google Drive, S3, Dropbox, OneDrive, SFTP, and 70+ others — with explicit include/exclude filtering.

**Status:** Released **v1.0.0** (May 2026). Open source under MIT license.

> Portfolio project. The point isn't the file-sync service itself — it's that it was built end-to-end by AI under direction, in six weeks, with zero lines of code written by me. The [case study](/publications/shipped-go-without-knowing-go/) is the substance.

## Key properties

- **On-write detection** via Windows `ReadDirectoryChangesW` (no polling)
- **Selective filtering** with per-project `.syncignore` files using `.gitignore` semantics
- **Bandwidth-efficient** via MD5 checksum comparison and a deduplicating fair queue
- **Single binary** with zero runtime dependencies (statically-linked SQLite)
- **Backend-agnostic** through `rclone` — 70+ cloud and remote backends
- **Configurable delete policy:** ignore, mirror, or quarantine
- **Background modes:** Windows Service (admin) or per-user Scheduled Task (no admin)
- **Self-update flow** with rclone auto-provisioning

## Scale at v1.0.0

- 282 git commits across 8 tagged releases (v0.4.0 → v1.0.0)
- ~22,800 production Go lines + ~31,800 test Go lines
- 1,060 Go test/fuzz functions
- 216 BugTracker records (with 75 from independent cross-AI review)
- ~10,700 lines of documentation
- ISO-aligned engineering: Requirements (29148), Quality Model (25010), Quality Measurement (25023), Testing (29119)

## Project links

- **Repository:** [github.com/qraveh/SelectiveMirror](https://github.com/qraveh/SelectiveMirror)
- **All releases:** [GitHub Releases](https://github.com/qraveh/SelectiveMirror/releases/)
- **v1.0.0 release notes:** [v1.0.0 tag](https://github.com/qraveh/SelectiveMirror/releases/tag/v1.0.0)
- **Windows installer:** [SelectiveMirror.msi](https://github.com/qraveh/SelectiveMirror/releases/download/v1.0.0/SelectiveMirror.msi)

## Read more

[**I Shipped a Production Go Project Without Knowing Go**]({{< ref "/publications/shipped-go-without-knowing-go.md" >}}) — a case study on AI-assisted software development, written from the experience of building SelectiveMirror.
