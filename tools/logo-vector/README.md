# Vector redraw of the Qodeh logo

Reproducible trace of `static/logo.png` (the canonical PNG master, 2432 × 2504) into SVG.

```bash
python tools/logo-vector/vectorize.py static/logo.png <out-dir>          # writes logo-full.svg + report.json
python tools/logo-vector/compare.py static/logo.png <out-dir>/logo-full.svg <work-dir> "<path to msedge.exe>"
```

`vectorize.py` traces the 50 % opacity line (the master's edges are feathered), fits Bézier curves with sharp
corners rebuilt where two straight edges meet, measures the gradients on the master (15 stops for the bands; one
gradient per letter, opacity ramp included) and redraws the stars as points of light clipped to the bands.
`compare.py` renders the SVG with headless Edge and scores it against the master on white and on black, and writes
side-by-side strips at 32, 200 and 1200 px.

Status (2026-10-11): candidate for the editor's review; the PNG master stays canonical. Not reproduced: the
faint star dust between the stars. Needs numpy, scipy, Pillow, contourpy (the last ships with matplotlib).
