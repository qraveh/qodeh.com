"""Tests for the self-hosted STIX Two Text subsets (QS-003). Run from the repo root: python tools/fonts/test_fonts.py
Needs fontTools and brotli. Checks what the browser relies on: the features, the coverage, the weight axis, the
licence fields, and that fonts.css names exactly the files that ship."""
import glob, os, re, unittest

from fontTools.ttLib import TTFont

DIR = os.path.join("static", "fonts", "stix-two-text")
CSS = os.path.join("assets", "css", "extended", "fonts.css")
# Small caps, figure styles and ligatures are kept in the latin subset only (build_stix.py); every subset keeps kern.
LATIN = {"ccmp", "locl", "smcp", "c2sc", "onum", "pnum", "liga", "frac", "sups", "subs"}
PROBES = {"latin": "AZaz09&", "latin-ext": "ŁŒ", "greek": "αβΩ", "cyrillic": "ЖжЯя"}


class StixSubsets(unittest.TestCase):
    def files(self):
        found = sorted(glob.glob(os.path.join(DIR, "*.woff2")))
        self.assertEqual(len(found), 8, found)
        return found

    def test_features_coverage_axis_licence(self):
        for path in self.files():
            with self.subTest(path=path):
                f = TTFont(path)
                subset_name = re.search(r"stix-two-text-([a-z-]+)-(normal|italic)\.woff2$", path).group(1)
                if subset_name == "latin":
                    feats = {r.FeatureTag for r in f["GSUB"].table.FeatureList.FeatureRecord}
                    self.assertTrue(LATIN <= feats, f"missing {sorted(LATIN - feats)}")
                self.assertIn("kern", {r.FeatureTag for r in f["GPOS"].table.FeatureList.FeatureRecord})
                cmap = f.getBestCmap()
                for ch in PROBES[subset_name]:
                    self.assertIn(ord(ch), cmap, ch)
                axes = {a.axisTag: (a.minValue, a.maxValue) for a in f["fvar"].axes}
                self.assertEqual(axes.get("wght"), (400.0, 700.0))
                ids = {r.nameID for r in f["name"].names}
                self.assertTrue({0, 13, 14} <= ids, "copyright/licence name records dropped")

    def test_small_caps_are_real_glyphs(self):
        # The files carry no glyph names (post format 3), so follow the smcp lookups: 'a' and 'z' must map to
        # glyphs of their own, i.e. the browser gets drawn small caps instead of synthesising scaled capitals.
        for style in ("normal", "italic"):
            f = TTFont(os.path.join(DIR, f"stix-two-text-latin-{style}.woff2"))
            gsub, cmap = f["GSUB"].table, f.getBestCmap()
            mapping = {}
            for rec in gsub.FeatureList.FeatureRecord:
                if rec.FeatureTag == "smcp":
                    for i in rec.Feature.LookupListIndex:
                        for st in gsub.LookupList.Lookup[i].SubTable:
                            st = getattr(st, "ExtSubTable", st)
                            mapping.update(getattr(st, "mapping", {}) or {})
            for ch in "az":
                self.assertIn(cmap[ord(ch)], mapping, f"{style}: no smcp glyph for {ch!r}")
                self.assertNotEqual(mapping[cmap[ord(ch)]], cmap[ord(ch)])

    def test_css_names_exactly_the_shipped_files(self):
        css = open(CSS, encoding="utf-8").read()
        named = set(re.findall(r"/fonts/stix-two-text/([\w-]+\.woff2)", css))
        self.assertEqual(named, {os.path.basename(p) for p in self.files()})
        self.assertTrue(os.path.exists(os.path.join(DIR, "OFL.txt")))


if __name__ == "__main__":
    unittest.main(verbosity=1)
