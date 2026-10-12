"""Build the site search's index: the site's own pages and the Quantum Technology Atlas's records, one file per scope.

The search (assets/js/qsearch.js) is the Atlas's Find carried over to the whole site (the editor's Q49 (b), 2026-10-11):
a regular expression, case-sensitive or not, substring or whole word, over the site's pages and the Atlas's records —
technologies, machines, organisations, architectures and the glossary — grouped by kind, each hit linking straight to
its page. The index is preloaded at idle (unless Save-Data), so a search answers as one types.

Inputs are built output only, never the Atlas's generator: the site's pages as Hugo rendered them (title from the h1,
description from the meta description, text from the page body: div.post-content, or the home page's introduction —
Hugo's own index.json leaves out pages marked `build: list: never`, such as About) and the Atlas's record pages as the deploy assembles them under public/publications/quantum-technology-atlas/ (title from
h1.rectitle, description from the meta description, text from <main class="recmain">); the glossary comes from the
pinned Atlas commit's data/glossary-own.json and data/glossary-field.json (the same two files its Glossary is built from).

Writes, under public/search/:
  site.json            the site's pages: {"t": title, "u": URL path, "k": kind, "d": description, "x": text}
  atlas-<lang>.json    one per Atlas language, the light tier preloaded at idle: the records without their text
                       ({"t", "u", "k", "d"}) and "g", the glossary [{"t": term, "d": definition, "u": that language's Atlas}]
  atlas-<lang>-text.json  the records' full text, {"x": [text, ...]} in the order of atlas-<lang>.json's "docs",
                       fetched when the search opens (≈1 MB compressed in English: too much to preload on every visit)
Stdlib only (runs in the deploy and locally).

Usage: python scripts/build_search_index.py <public-dir> [--glossary <qt-map data dir>]
"""
import argparse, html, json, os, re, sys
from html.parser import HTMLParser

ATLAS = "publications/quantum-technology-atlas"
KINDS = ("technology", "machine", "organisation", "architecture")
SITE_KIND = {"publications": "publication", "projects": "project", "lectures": "lecture"}
SKIP_SITE = re.compile(r"^/(search|tags|categories|_[^/]*)(/|$)|/page/\d+/$")


class RecordPage(HTMLParser):
    """Title, description, language and the text of <main class="recmain"> of one Atlas record page. The title is
    h1.rectitle without its span.recid (the record's id, or "on the map bar: …"); the h1 is not repeated in the text."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang, self.desc, self.title, self.parts = "", "", "", []
        self._main = 0          # depth inside <main class="recmain">
        self._skip = 0          # inside <script>/<style>
        self._h1 = False
        self._recid = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self._recid:
            self._recid += 1
        elif tag == "span" and "recid" in (a.get("class") or "").split():
            self._recid = 1
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")
        if tag in ("script", "style"):
            self._skip += 1
        if self._main:
            self._main += 1
            if tag in ("p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "h4", "section", "br", "table"):
                self.parts.append(" ")
        elif tag == "main" and "recmain" in (a.get("class") or "").split():
            self._main = 1
        if tag == "h1" and "rectitle" in (a.get("class") or "").split():
            self._h1 = True

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1
        if self._main:
            self._main -= 1
        if self._recid:
            self._recid -= 1
        if tag == "h1":
            self._h1 = False

    def handle_data(self, data):
        if self._skip:
            return
        if self._h1:
            if not self._recid:
                self.title += data
            return
        if self._main:
            self.parts.append(data)


def squash(s):
    return re.sub(r"\s+", " ", s or "").strip()


class SitePage(HTMLParser):
    """Title, description and body text of one page Hugo rendered (PaperMod's markup); `refresh` marks a redirect stub."""
    BODY = ("post-content",)

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.desc, self.title, self.doc_title, self.parts, self.refresh = "", "", "", [], False
        self._body = 0
        self._skip = 0
        self._h1 = self._in_title = False
        self._home = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = (a.get("class") or "").split()
        if tag == "meta":
            if a.get("name") == "description":
                self.desc = a.get("content", "")
            if (a.get("http-equiv") or "").lower() == "refresh":
                self.refresh = True
        if tag == "title":
            self._in_title = True
        if tag in ("script", "style", "svg"):
            self._skip += 1
        if tag == "h1" and not self.title:
            self._h1 = True
        if self._body and tag in ("footer", "nav"):
            # minified HTML omits optional end tags (</p>, </li>), so the depth count cannot find the body's end:
            # PaperMod's post footer (tags, previous/next) and navigation follow the body, and end it
            self._body = 0
        elif self._body:
            self._body += 1
            if tag in ("p", "div", "li", "tr", "td", "th", "h2", "h3", "h4", "br", "table", "blockquote", "pre"):
                self.parts.append(" ")
        elif tag == "div" and (set(cls) & set(self.BODY) or (self._home and "entry-content" in cls)):
            self._body = 1
        if tag == "article" and "home-info" in cls:
            self._home = 1
        elif self._home:
            self._home += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "svg") and self._skip:
            self._skip -= 1
        if self._body:
            self._body -= 1
        if self._home:
            self._home -= 1
        if tag == "h1":
            self._h1 = False
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._skip:
            return
        if self._in_title:
            self.doc_title += data
        if self._h1:
            self.title += data
        if self._body:
            self.parts.append(data)


def site_docs(public):
    """Every page of the site but the Atlas, the taxonomy and pagination pages, the search page and redirect stubs."""
    docs = []
    for dirpath, dirnames, filenames in os.walk(public):
        rel = os.path.relpath(dirpath, public).replace(os.sep, "/")
        rel = "" if rel == "." else rel
        if rel.startswith(ATLAS) or rel.startswith("search"):
            dirnames[:] = []
            continue
        if "index.html" not in filenames:
            continue
        u = "/" + (rel + "/" if rel else "")
        if SKIP_SITE.search(u):
            continue
        p = SitePage()
        p.feed(open(os.path.join(dirpath, "index.html"), encoding="utf-8").read())
        if p.refresh:
            continue
        sec = rel.split("/")[0] if rel else ""
        kind = SITE_KIND.get(sec, "page") if "/" in rel else "page"     # a section's own list page is a page
        title = squash(p.title) or squash(p.doc_title.split("|")[0])
        docs.append({"t": title, "u": u, "k": kind, "d": squash(p.desc), "x": squash("".join(p.parts))})
    docs.sort(key=lambda d: d["u"])
    return docs


def atlas_docs(public):
    """{lang: [record documents]} from the record pages under public/<ATLAS>/[<lang>/]<kind>/<id>.html."""
    root = os.path.join(public, ATLAS.replace("/", os.sep))
    out = {}
    if not os.path.isdir(root):
        return out
    folders = [""] + [d + "/" for d in sorted(os.listdir(root)) if os.path.isdir(os.path.join(root, d, "machine"))]
    for folder in folders:
        for kind in KINDS:
            kdir = os.path.join(root, folder.replace("/", os.sep), kind)
            if not os.path.isdir(kdir):
                continue
            for fn in sorted(os.listdir(kdir)):
                if not fn.endswith(".html") or fn == "index.html":
                    continue
                p = RecordPage()
                p.feed(open(os.path.join(kdir, fn), encoding="utf-8").read())
                lang = p.lang or (folder.strip("/") or "en")
                out.setdefault(lang, []).append({
                    "t": squash(p.title), "u": f"/{ATLAS}/{folder}{kind}/{fn}", "k": kind,
                    "d": squash(p.desc), "x": squash("".join(p.parts))})
    return out


def glossary(data_dir, langs, folders):
    """{lang: [{t, d, u}]}: the Atlas's Glossary as its page lists it (build_html.glossary_html): the term's forms in the
    language, else its English forms, else its id; the definition in the language, else English."""
    entries = []
    for fn in ("glossary-own.json", "glossary-field.json"):
        p = os.path.join(data_dir, fn)
        if os.path.exists(p):
            entries += json.load(open(p, encoding="utf-8"))
    out = {}
    for L in langs:
        rows = []
        for e in entries:
            forms = e.get("match" if L == "en" else "match_" + L) if e.get(L) else None
            forms = forms or e.get("match") or [e["id"]]
            term = forms[0].strip()
            term = term[:1].upper() + term[1:] if term[:1].isalpha() else term
            definition = e.get(L) or e.get("en")
            if definition and "{{" not in definition:     # placeholders are filled by the Atlas build; such rows wait for it
                rows.append({"t": term, "d": squash(definition), "u": f"/{ATLAS}/{folders.get(L, '')}"})
        out[L] = rows
    return out


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    open(path, "w", encoding="utf-8", newline="\n").write(data)
    return len(data.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("public")
    ap.add_argument("--glossary", help="the pinned Atlas commit's data/ directory (glossary-own.json, glossary-field.json)")
    a = ap.parse_args()
    out_dir = os.path.join(a.public, "search")
    n = write(os.path.join(out_dir, "site.json"), {"v": 1, "docs": site_docs(a.public)})
    print(f"search/site.json: {n:,} B")
    records = atlas_docs(a.public)
    folders = {L: ("" if L == "en" else L + "/") for L in records}
    gloss = glossary(a.glossary, list(records), folders) if a.glossary else {}
    for L, docs in sorted(records.items()):
        light = [{k: d[k] for k in ("t", "u", "k", "d")} for d in docs]
        n = write(os.path.join(out_dir, f"atlas-{L}.json"), {"v": 1, "lang": L, "docs": light, "g": gloss.get(L, [])})
        m = write(os.path.join(out_dir, f"atlas-{L}-text.json"), {"v": 1, "lang": L, "x": [d["x"] for d in docs]})
        kinds = {k: sum(1 for d in docs if d["k"] == k) for k in KINDS}
        print(f"search/atlas-{L}.json: {n:,} B, -text.json {m:,} B; {kinds}, glossary {len(gloss.get(L, []))}")
    if not records:
        print("no Atlas record pages found: the search covers the site only", file=sys.stderr)


if __name__ == "__main__":
    main()
