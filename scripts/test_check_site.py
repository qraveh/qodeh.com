"""Tests for check_site.py: one synthetic site that passes, then one breakage per rule. Run: python scripts/test_check_site.py"""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check_site.py")

GOOD_PAGE = """<!doctype html><html><head><title>t</title><link rel="stylesheet" href="/css/site.css">
<meta name="citation_title" content="Monitor"><meta name="citation_author" content="Neeman, Raveh">
<meta name="citation_publication_date" content="2026/09/06"><meta name="citation_pdf_url" content="https://qodeh.com/f.pdf">
<meta name="citation_doi" content="10.5281/zenodo.21860767">
<script type="application/ld+json">{"@type":"Report"}</script></head>
<body><a href="/about/">About</a> <a href="https://qodeh.com/about/#me">me</a> <a href="https://example.org/x">ext</a>
<a href="mailto:a@b.c">mail</a> <p>Costs $10 B and $5 M.</p> <code>x^{2}</code> <img src="/img/small.png" alt="">
<math><msup><mi>x</mi><mn>2</mn></msup></math></body></html>"""


def write(root, rel, data, binary=False):
    p = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb" if binary else "w", **({} if binary else {"encoding": "utf-8"})).write(data)


class CheckSite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.site, self.contract = os.path.join(self.tmp, "public"), os.path.join(self.tmp, "contract")
        write(self.contract, "frozen-urls.txt", "/\n/about/\n/sfq-monitor/\n[atlas] /publications/quantum-technology-atlas/\n")
        write(self.contract, "citation-pages.txt", "/sfq-monitor/ citation_title citation_author citation_publication_date citation_pdf_url citation_doi\n")
        write(self.contract, "budget.json", json.dumps({"page_kb": 150, "image_warn_kb": 500, "exclude_prefixes": ["/publications/quantum-technology-atlas/"]}))
        write(self.site, "index.html", GOOD_PAGE)
        write(self.site, "sfq-monitor/index.html", GOOD_PAGE)
        write(self.site, "about/index.html", '<html><body><h1 id="me">Me</h1><a href="../">home</a></body></html>')
        write(self.site, "css/site.css", "body{font-family:x}@font-face{src:url(/fonts/f.woff2)}")
        write(self.site, "fonts/f.woff2", b"\0" * 20000, binary=True)
        write(self.site, "img/small.png", b"\0" * 1000, binary=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_check(self, *extra):
        r = subprocess.run([sys.executable, "-I", CHECK, self.site, "--json", "--contract", self.contract, *extra], capture_output=True, text=True, encoding="utf-8")
        return r.returncode, json.loads(r.stdout)

    def rules(self, out):
        return {f[0] for f in out["failures"]}

    def test_good_site_passes(self):
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out)
        self.assertEqual(out["summary"]["atlas_frozen_skipped"], 1)

    def test_frozen_missing(self):
        os.remove(os.path.join(self.site, "about", "index.html"))
        rc, out = self.run_check()
        self.assertEqual(rc, 1)
        self.assertIn("frozen", self.rules(out))

    def test_atlas_required_with_flag(self):
        rc, out = self.run_check("--with-atlas")
        self.assertEqual(rc, 1)
        self.assertTrue(any(f[0] == "frozen" and "quantum-technology-atlas" in f[1] for f in out["failures"]))

    def test_citation_meta_missing(self):
        write(self.site, "sfq-monitor/index.html", GOOD_PAGE.replace('name="citation_doi"', 'name="x"'))
        rc, out = self.run_check()
        self.assertIn("citation", self.rules(out))

    def test_citation_jsonld_broken(self):
        write(self.site, "sfq-monitor/index.html", GOOD_PAGE.replace('{"@type":"Report"}', '{"@type":'))
        rc, out = self.run_check()
        self.assertIn("citation", self.rules(out))

    def test_broken_internal_link(self):
        write(self.site, "about/index.html", '<html><body><h1 id="me">Me</h1><a href="/nowhere/">x</a></body></html>')
        rc, out = self.run_check()
        self.assertIn("links", self.rules(out))

    def test_missing_fragment_is_warning_only(self):
        write(self.site, "index.html", GOOD_PAGE.replace("#me", "#nobody"))
        rc, out = self.run_check()
        self.assertEqual(rc, 0)
        self.assertTrue(any(w[0] == "fragment" for w in out["warnings"]))

    def test_budget_counts_fonts(self):
        write(self.site, "fonts/f.woff2", b"\0" * 200000, binary=True)
        rc, out = self.run_check()
        self.assertIn("budget", self.rules(out))

    def test_unicode_range_subsets_counted_only_when_used(self):
        write(self.site, "css/site.css", "@font-face{font-family:t;src:url(/fonts/lat.woff2);unicode-range:U+0000-00FF}"
                                         "@font-face{font-family:t;src:url(/fonts/cyr.woff2);unicode-range:U+0400-045F}")
        write(self.site, "fonts/lat.woff2", b"\0" * 20000, binary=True)
        write(self.site, "fonts/cyr.woff2", b"\0" * 200000, binary=True)
        rc, out = self.run_check()
        self.assertEqual(rc, 0, out)                       # Latin-only pages never fetch the 200 KB Cyrillic subset
        write(self.site, "about/index.html", '<html><head><link rel="stylesheet" href="/css/site.css"></head><body><h1 id="me">Русский</h1></body></html>')
        rc, out = self.run_check()
        self.assertIn("budget", self.rules(out))           # a page that uses Cyrillic does

    def test_unrendered_tex(self):
        write(self.site, "about/index.html", '<html><body><h1 id="me">Me</h1><p>so e^{iφ} leaks</p></body></html>')
        rc, out = self.run_check()
        self.assertIn("formulas", self.rules(out))

    def test_dollar_math_but_not_currency(self):
        write(self.site, "about/index.html", '<html><body><h1 id="me">Me</h1><p>where $x_1$ grows; it cost $10 B</p></body></html>')
        rc, out = self.run_check()
        hits = [f for f in out["failures"] if f[0] == "formulas"]
        self.assertEqual(len(hits), 1, hits)

    def test_katex_error_span(self):
        write(self.site, "about/index.html", '<html><body><h1 id="me">Me</h1><span class="katex-error">\\frac{</span></body></html>')
        rc, out = self.run_check()
        self.assertIn("formulas", self.rules(out))

    def test_big_image_warns(self):
        write(self.site, "img/small.png", b"\0" * 600000, binary=True)
        rc, out = self.run_check()
        self.assertEqual(rc, 0)
        self.assertTrue(any(w[0] == "image" for w in out["warnings"]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
