# tools/fonts — STIX Two Text, parked for formula-rich texts

The site uses PaperMod's system font stack: Segoe UI on Windows, San Francisco on Apple devices, Roboto on
Android. That was the editor's choice on 2026-10-11, after trying STIX Two Text site-wide on the redesign branch
(commits `0bd1fb3`..`ee70dbf`, BugTracker QS-003). STIX is kept for texts where formulas begin, such as the
Atlas (its own build, in `qraveh/qt-map`).

- `build_stix.py --out DIR` takes the upstream `stipub/stixfonts` v2.13b171 variable woff2 files, pinned by
  SHA-256, and subsets them locally. It keeps Google's four unicode-range splits, and the latin subset keeps
  small caps and figure styles. It writes `DIR/*.woff2`, `DIR/OFL.txt` and `DIR/stix-two-text.css`, and never
  writes into the site.
- `test_fonts.py DIR` checks the result: features, real small-caps glyphs, coverage, the weight axis, the
  licence fields, and that the CSS names exactly the files. Needs fontTools and brotli.
