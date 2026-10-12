"""Tests for build_search_index.py: a synthetic built site and Atlas. Run: python scripts/test_build_search_index.py"""
import json, os, shutil, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build_search_index.py")
ATLAS = "publications/quantum-technology-atlas"


def write(root, rel, text):
    p = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def dump(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)


def page(title, desc, body, footer=""):
    # PaperMod's markup, minified the way Hugo does it: optional end tags (</p>, </li>) are left out
    return (f'<!doctype html><html lang=en><head><title>{title} | Raveh Neeman</title><meta name=description content="{desc}">'
            f'</head><body><header class=header><nav class=nav><ul id=menu><li><a href=/search/>Search</a></ul></nav></header>'
            f'<main class=main><article class=post-single><header class=post-header><h1 class=post-title>{title}</h1></header>'
            f'<div class="post-content md-content">{body}</div><footer class=post-footer>{footer}</footer></article></main>'
            f'<footer class=footer>© 2021–2026 Qodeh</footer></body></html>')


def record(lang, title, desc, body):
    return (f'<!doctype html><html lang="{lang}" dir="ltr"><head><title>{title} — Atlas</title>'
            f'<meta name="description" content="{desc}"></head><body><div id="app"><div class="recbar">'
            f'<a href="../index.html">← Quantum Technology Atlas</a></div><main class="recmain"><h1 class="rectitle">{title}</h1>'
            f'<section class="card"><div class="mc">{body}</div></section></main></div></body></html>')


class BuildSearchIndex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        P = self.pub = os.path.join(self.tmp, "public")
        write(P, "index.html", '<html><head><meta name=description content="Personal site"></head><body><main>'
                               '<article class="first-entry home-info"><header class=entry-header><h1>Raveh Neeman</h1></header>'
                               '<div class="entry-content md-content"><p>Quantum computing researcher<p>Mission: architect, then build</div>'
                               '<footer class=entry-footer><div class=social-icons>LinkedIn</div></footer></article></main></body></html>')
        write(P, "about/index.html", page("About", "Who", "<p>Thirty tapeouts<p>Five years of quantum", "tag-chip « Prev Other page"))
        write(P, "publications/index.html", page("Publications", "Editions", ""))
        write(P, "publications/monitor/index.html", page("Monitor", "SCE", "<p>Josephson junctions <ul><li>one<li>two</ul>"))
        write(P, "publications/page/1/index.html", '<html><head><meta http-equiv="refresh" content="0; url=/publications/"></head></html>')
        write(P, "qt-map/index.html", '<html><head><title>Atlas</title><meta http-equiv=refresh content="0; url=/publications/quantum-technology-atlas/"></head></html>')
        write(P, "tags/go/index.html", page("Go", "", "<p>tag page"))
        write(P, "search/index.html", page("Search this site", "", ""))
        write(P, f"{ATLAS}/machine/m1.html", record("en", "Machine One", "Org — 20 qubits", "laser trimming tunes qubits"))
        write(P, f"{ATLAS}/machine/index.html", record("en", "Machines", "", "the list"))
        write(P, f"{ATLAS}/technology/transmon.html", record("en", 'Transmon <span class="recid">transmon</span>', "a carrier", "Koch 2007"))
        write(P, f"{ATLAS}/ru/machine/m1.html", record("ru", "Машина один", "Орг — 20 кубитов", "лазерная подгонка"))
        write(P, f"{ATLAS}/ru/technology/transmon.html", record("ru", "Трансмон", "носитель", "Кох 2007"))
        self.data = os.path.join(self.tmp, "data")
        os.makedirs(self.data)
        dump(os.path.join(self.data, "glossary-own.json"),
             [{"id": "qual-D", "match": ["[D]"], "match_ru": ["[D]"], "en": "Demonstrated", "ru": "Продемонстрировано"}])
        dump(os.path.join(self.data, "glossary-field.json"),
             [{"id": "abbr-t1", "match": ["T1"], "en": "Energy-relaxation time"},                       # no Russian: English in ru
              {"id": "count", "match": ["N"], "en": "There are {{machines}} machines", "ru": "{{machines}} машин"}])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build(self, *extra):
        r = subprocess.run([sys.executable, "-I", BUILD, self.pub, *extra], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        def load(n):
            with open(os.path.join(self.pub, "search", n), encoding="utf-8") as fh:
                return json.load(fh)
        return load

    def test_site_pages_and_skips(self):
        site = self.build("--glossary", self.data)("site.json")["docs"]
        urls = {d["u"]: d for d in site}
        self.assertEqual(sorted(urls), ["/", "/about/", "/publications/", "/publications/monitor/"])
        self.assertEqual(urls["/publications/monitor/"]["k"], "publication")
        self.assertEqual(urls["/publications/"]["k"], "page")                  # a section's own list page
        self.assertIn("Thirty tapeouts", urls["/about/"]["x"])
        self.assertNotIn("Prev", urls["/about/"]["x"])                         # the post footer is not the body
        self.assertNotIn("Qodeh", urls["/about/"]["x"])
        self.assertIn("architect, then build", urls["/"]["x"])
        self.assertNotIn("LinkedIn", urls["/"]["x"])
        self.assertEqual(urls["/about/"]["d"], "Who")

    def test_atlas_tiers_and_languages(self):
        load = self.build("--glossary", self.data)
        en, en_x = load("atlas-en.json"), load("atlas-en-text.json")
        self.assertEqual({d["u"] for d in en["docs"]}, {f"/{ATLAS}/machine/m1.html", f"/{ATLAS}/technology/transmon.html"})
        self.assertNotIn("x", en["docs"][0])                                   # the light tier carries no text
        self.assertEqual(len(en_x["x"]), len(en["docs"]))                      # the text tier aligns with it, in order
        i = [d["u"] for d in en["docs"]].index(f"/{ATLAS}/machine/m1.html")
        self.assertIn("laser trimming", en_x["x"][i])
        self.assertNotIn("← Quantum Technology Atlas", en_x["x"][i])           # the record bar is outside <main>
        t = [d["u"] for d in en["docs"]].index(f"/{ATLAS}/technology/transmon.html")
        self.assertEqual(en["docs"][t]["t"], "Transmon")                       # the id span is not the title
        self.assertNotIn("Transmon", en_x["x"][t])                             # and the h1 is not repeated in the text
        ru = load("atlas-ru.json")
        self.assertEqual({d["t"] for d in ru["docs"]}, {"Машина один", "Трансмон"})
        self.assertTrue(all(d["u"].startswith(f"/{ATLAS}/ru/") for d in ru["docs"]))

    def test_glossary(self):
        load = self.build("--glossary", self.data)
        en, ru = load("atlas-en.json")["g"], load("atlas-ru.json")["g"]
        self.assertEqual([g["t"] for g in en], ["[D]", "T1"])                  # the placeholder entry waits for the Atlas build
        self.assertEqual({g["t"]: g["d"] for g in ru}, {"[D]": "Продемонстрировано", "T1": "Energy-relaxation time"})
        self.assertEqual({g["u"] for g in ru}, {f"/{ATLAS}/ru/"})

    def test_without_atlas(self):
        shutil.rmtree(os.path.join(self.pub, "publications", "quantum-technology-atlas"))
        load = self.build()
        self.assertTrue(load("site.json")["docs"])
        self.assertFalse(os.path.exists(os.path.join(self.pub, "search", "atlas-en.json")))


if __name__ == "__main__":
    unittest.main(verbosity=1)
