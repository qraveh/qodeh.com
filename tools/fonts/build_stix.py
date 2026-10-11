"""Self-host STIX Two Text (SIL OFL 1.1): take the upstream release and subset it locally, keeping its features.

Source: stipub/stixfonts, tag v2.13b171, fonts/variable_ttf_woff2/ (one variable file per style, wght 400-700),
pinned by SHA-256 below. Google Fonts' served subsets were used before and drop smcp/c2sc/onum/sups/subs/case,
so the menu's small caps came out browser-synthesised (BugTracker QS-003). Here every feature the site may use
is kept. The output keeps Google's four unicode-range splits, so a page fetches a subset only when it uses
those characters. The name table is kept whole, so the copyright and licence fields travel with each file,
and OFL.txt ships beside the fonts.

Usage: python tools/fonts/build_stix.py [--cache DIR]   (run from the repo root; needs fontTools and brotli)
Writes static/fonts/stix-two-text/*.woff2 + OFL.txt and assets/css/extended/fonts.css; re-running replaces them.
The upstream files are downloaded once into the cache directory (default: a temp folder) and verified there.
"""
import argparse, hashlib, os, re, shutil, tempfile, urllib.request

from fontTools import subset

TAG = "v2.13b171"
BASE = f"https://raw.githubusercontent.com/stipub/stixfonts/{TAG}/"
SOURCES = {  # style -> (path in the upstream repo, SHA-256)
    "normal": ("fonts/variable_ttf_woff2/STIXTwoText%5Bwght%5D.woff2",
               "e2a13a91ad5d98da25a6972e8b19ce216e1997037004d9051290d0094b10a58b"),
    "italic": ("fonts/variable_ttf_woff2/STIXTwoText-Italic%5Bwght%5D.woff2",
               "a5e3f5f788a93cd23f015f6d6e1cc64b3239ad0a798aec5032c6be18e165f78d"),
}
LICENSE = ("OFL.txt", "0c8825913b60d858aacdb33c4ca6660a7d64b0d6464702efbb19313f5765861a")

# Google Fonts' unicode-range splits for STIX Two Text (as served in 2026-10), kept so pages load the same subsets.
SUBSETS = {
    "latin": "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, "
             "U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
    "latin-ext": "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, "
                 "U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, "
                 "U+A720-A7FF",
    "greek": "U+0370-0377, U+037A-037F, U+0384-038A, U+038C, U+038E-03A1, U+03A3-03FF",
    "cyrillic": "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116",
}
# Kept layout features. Left out everywhere: cv01-cv03 and ss01-ss02 (alternate letterforms the site does not use).
# Small caps and figure styles are kept in the latin subset only (the menu, labels and figures are Latin); in
# the other subsets they would add ~7 KB per file for Cyrillic/Greek small caps the site never sets.
BASE_FEATURES = ["ccmp", "locl", "liga", "kern", "mark", "mkmk"]
LATIN_FEATURES = BASE_FEATURES + ["frac", "numr", "dnom", "smcp", "c2sc", "onum", "pnum", "sups", "subs", "case"]
OUT_DIR = os.path.join("static", "fonts", "stix-two-text")
CSS_OUT = os.path.join("assets", "css", "extended", "fonts.css")


def parse_ranges(spec):
    cps = set()
    for part in spec.split(","):
        m = re.fullmatch(r"\s*U\+([0-9A-Fa-f]+)(?:-([0-9A-Fa-f]+))?\s*", part)
        lo = int(m.group(1), 16)
        cps.update(range(lo, int(m.group(2) or m.group(1), 16) + 1))
    return cps


def fetch(rel, sha, cache):
    path = os.path.join(cache, os.path.basename(rel).replace("%5B", "[").replace("%5D", "]"))
    if not os.path.exists(path):
        with urllib.request.urlopen(BASE + rel, timeout=60) as r:
            open(path, "wb").write(r.read())
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if got != sha:
        raise SystemExit(f"SHA-256 mismatch for {path}: {got} (expected {sha})")
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(tempfile.gettempdir(), f"stix-src-{TAG}"))
    cache = ap.parse_args().cache
    os.makedirs(cache, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    def options(name):
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = LATIN_FEATURES if name == "latin" else BASE_FEATURES
        opts.name_IDs = ["*"]
        opts.name_languages = ["*"]
        opts.notdef_outline = True
        return opts

    css = [f"/* STIX Two Text, SIL Open Font License 1.1 (stipub/stixfonts {TAG}; licence: /fonts/stix-two-text/OFL.txt), "
           "subset locally by tools/fonts/build_stix.py with small caps and figure styles kept. */"]
    total = 0
    for style, (rel, sha) in SOURCES.items():
        src = fetch(rel, sha, cache)
        for name, spec in SUBSETS.items():
            opts = options(name)
            font = subset.load_font(src, opts)
            sub = subset.Subsetter(opts)
            sub.populate(unicodes=parse_ranges(spec))
            sub.subset(font)
            out = f"stix-two-text-{name}-{style}.woff2"
            subset.save_font(font, os.path.join(OUT_DIR, out), opts)
            size = os.path.getsize(os.path.join(OUT_DIR, out))
            total += size
            print(f"{size:7d}  {out}")
            css.append("@font-face{font-family:'STIX Two Text';font-style:%s;font-weight:400 700;font-display:swap;"
                       "src:url(/fonts/stix-two-text/%s) format('woff2');unicode-range:%s}" % (style, out, spec))
    shutil.copyfile(fetch(LICENSE[0], LICENSE[1], cache), os.path.join(OUT_DIR, "OFL.txt"))
    open(CSS_OUT, "w", encoding="utf-8", newline="\n").write("\n".join(css) + "\n")
    print(f"{total} bytes in {len(SOURCES) * len(SUBSETS)} files; {len(css) - 1} @font-face rules -> {CSS_OUT}")


if __name__ == "__main__":
    main()
