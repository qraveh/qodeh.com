#!/usr/bin/env python3
"""Check a built qodeh.com against its contract (contract/*.txt, contract/budget.json).

Rules (each failure makes the run exit 1; warnings never do):
  frozen     every path in contract/frozen-urls.txt resolves in the build
  citation   pages in contract/citation-pages.txt carry the required citation_* meta and a parseable JSON-LD graph
  links      every internal href/src on a site page resolves to a file in the build
  budget     HTML + CSS + JS (gzip) + fonts (as stored) per page stay within budget.json page_kb
  formulas   no unrendered TeX ($…$, ^{…}, _{…}) in visible text, no KaTeX error spans
Warnings: images above budget.json image_warn_kb; #fragments that point at no id on the target page.

Usage: python scripts/check_site.py <site-dir> [--with-atlas] [--json] [--contract DIR]
Standard library only, so the deploy workflow needs no installs.
"""
import argparse, gzip, json, os, re, sys
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

SITE_HOSTS = {"qodeh.com", "www.qodeh.com"}
ATLAS = "/publications/quantum-technology-atlas/"
TEXT_EXT = {".css", ".js", ".mjs"}
FONT_EXT = {".woff2", ".woff", ".ttf", ".otf"}
IMG_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico"}
TEX = re.compile(r"(?<![\w$])\$(?!\s)[^$\n]{1,200}?(?<!\s)\$(?![\w$])|[\^_]\{[^{}\n]{0,40}\}")


class Page(HTMLParser):
    """Collects what the checks need from one HTML document."""
    SKIP_TEXT = {"script", "style", "code", "pre", "kbd", "samp", "math", "svg", "textarea"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.meta, self.ids, self.ldjson, self.text = [], {}, set(), [], []
        self.katex_errors = 0
        self._skip, self._in_ld, self._ld = 0, False, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("id", "name"):
            if a.get(k) and (k == "id" or tag == "a"):
                self.ids.add(a[k])
        if "katex-error" in (a.get("class") or ""):
            self.katex_errors += 1
        for k in ("href", "src", "poster", "data"):
            if a.get(k):
                self.refs.append((tag, k, a[k], (a.get("rel") or "").lower()))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                u = part.strip().split(" ")[0]
                if u:
                    self.refs.append((tag, "srcset", u, ""))
        if tag == "meta" and a.get("name"):
            self.meta.setdefault(a["name"], []).append(a.get("content") or "")
        if tag == "script" and (a.get("type") or "").lower() == "application/ld+json":
            self._in_ld, self._ld = True, []
        if tag in self.SKIP_TEXT:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ld:
            self.ldjson.append("".join(self._ld))
            self._in_ld = False
        if tag in self.SKIP_TEXT and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_ld:
            self._ld.append(data)
        elif not self._skip:
            self.text.append(data)


def read_list(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def resolve(site, url_path):
    """Map a URL path to a file in the build, or None."""
    p = unquote(url_path)
    if p.endswith("/"):
        cand = [p + "index.html"]
    elif os.path.splitext(p)[1]:
        cand = [p]
    else:
        cand = [p + "/index.html", p + ".html", p]
    for c in cand:
        f = os.path.join(site, c.lstrip("/").replace("/", os.sep))
        if os.path.isfile(f):
            return f
    return None


def url_of(site, file):
    rel = os.path.relpath(file, site).replace(os.sep, "/")
    return "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)


def internal_path(ref, page_url):
    """Return (path, fragment) for an internal reference, or None for external/non-http ones."""
    if ref.startswith(("mailto:", "tel:", "sms:", "data:", "javascript:", "blob:")):
        return None
    s = urlsplit(ref)
    if s.scheme in ("http", "https"):
        if s.hostname not in SITE_HOSTS:
            return None
        path = s.path or "/"
    elif s.scheme:
        return None
    elif ref.startswith("//"):
        return None
    elif s.path.startswith("/"):
        path = s.path
    elif not s.path:
        path = page_url  # "#frag" or "?q" on the same page
    else:
        base = page_url if page_url.endswith("/") else page_url.rsplit("/", 1)[0] + "/"
        parts = []
        for seg in (base + s.path).split("/"):
            if seg == "..":
                parts = parts[:-1]
            elif seg != ".":
                parts.append(seg)
        path = "/".join(parts)
    return path, s.fragment


def gz(n_bytes):
    return len(gzip.compress(n_bytes, 9))


def main():
    try:  # reports carry non-ASCII (→, formulas); a Windows console defaults to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("site")
    ap.add_argument("--with-atlas", action="store_true", help="the Atlas has been assembled into the build")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--contract", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "contract"))
    args = ap.parse_args()
    site, C = os.path.abspath(args.site), os.path.abspath(args.contract)
    budget = json.load(open(os.path.join(C, "budget.json"), encoding="utf-8"))
    fails, warns = [], []

    # frozen URLs
    skipped_atlas = 0
    for line in read_list(os.path.join(C, "frozen-urls.txt")):
        atlas = line.startswith("[atlas]")
        path = line.split()[-1]
        if atlas and not args.with_atlas:
            skipped_atlas += 1
            continue
        if not resolve(site, path):
            fails.append(("frozen", path, "does not resolve in the build"))

    # parse every site page (the Atlas subtree has its own checks in qt-map)
    pages = {}
    for root, _dirs, files in os.walk(site):
        for fn in files:
            if fn.endswith(".html"):
                f = os.path.join(root, fn)
                u = url_of(site, f)
                if u.startswith(ATLAS):
                    continue
                p = Page()
                try:
                    p.feed(open(f, encoding="utf-8", errors="replace").read())
                except Exception as e:  # malformed HTML is itself a finding
                    fails.append(("parse", u, str(e)))
                    continue
                pages[u] = (f, p)

    # citation pages
    for line in read_list(os.path.join(C, "citation-pages.txt")):
        path, *names = line.split()
        if path not in pages:
            fails.append(("citation", path, "page missing from the build"))
            continue
        p = pages[path][1]
        for n in names:
            if not any(v.strip() for v in p.meta.get(n, [])):
                fails.append(("citation", path, f"missing or empty <meta name={n}>"))
        if not p.ldjson:
            fails.append(("citation", path, "no application/ld+json graph"))
        for blob in p.ldjson:
            try:
                json.loads(blob)
            except ValueError as e:
                fails.append(("citation", path, f"JSON-LD does not parse: {e}"))

    # links, fragments, budget, images, formulas
    file_cache, ids_cache, big_images = {}, {}, {}
    for u, (f, p) in sorted(pages.items()):
        own = open(f, "rb").read()
        weight, counted = gz(own), set()
        for tag, attr, ref, rel in p.refs:
            ip = internal_path(ref, u)
            if ip is None:
                continue
            path, frag = ip
            if path.startswith(ATLAS) and not args.with_atlas:
                continue
            target = resolve(site, path)
            if not target:
                if not (tag == "link" and rel in ("preconnect", "dns-prefetch")):
                    fails.append(("links", u, f"{tag}[{attr}] → {ref} does not resolve"))
                continue
            ext = os.path.splitext(target)[1].lower()
            if frag and ext == ".html" and not (target == f and frag in p.ids):
                if target not in ids_cache:
                    q = Page(); q.feed(open(target, encoding="utf-8", errors="replace").read()); ids_cache[target] = q.ids
                if frag not in ids_cache[target] and target != f:
                    warns.append(("fragment", u, f"{ref}: no id '{frag}' on the target page"))
                elif target == f and frag not in p.ids:
                    warns.append(("fragment", u, f"{ref}: no id '{frag}' on this page"))
            if target in counted:
                continue
            counted.add(target)
            if ext in TEXT_EXT and (tag in ("script", "link")):
                if target not in file_cache:
                    data = open(target, "rb").read()
                    fonts = set()
                    if ext == ".css":
                        for m in re.finditer(rb"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", data):
                            fu = m.group(1).decode("utf-8", "replace")
                            fip = internal_path(fu, url_of(site, target))
                            if fip:
                                ft = resolve(site, fip[0])
                                if ft and os.path.splitext(ft)[1].lower() in FONT_EXT:
                                    fonts.add(ft)
                    file_cache[target] = (gz(data), fonts)
                size, fonts = file_cache[target]
                weight += size
                for ft in fonts - counted:
                    counted.add(ft)
                    weight += os.path.getsize(ft)
            elif ext in FONT_EXT:
                weight += os.path.getsize(target)
            elif ext in IMG_EXT:
                kb = os.path.getsize(target) / 1024
                if kb > budget["image_warn_kb"]:
                    big_images.setdefault(url_of(site, target), [kb, set()])[1].add(u)
        if not any(u.startswith(x) for x in budget.get("exclude_prefixes", [])) and weight > budget["page_kb"] * 1024:
            fails.append(("budget", u, f"{weight / 1024:.0f} KB > {budget['page_kb']} KB (HTML/CSS/JS gzip + fonts)"))
        text = " ".join(p.text)
        for m in TEX.finditer(text):
            fails.append(("formulas", u, f"unrendered TeX: {m.group(0)[:60]!r}"))
        if p.katex_errors:
            fails.append(("formulas", u, f"{p.katex_errors} KaTeX error span(s)"))
    for img, (kb, refs) in sorted(big_images.items()):
        warns.append(("image", img, f"{kb:.0f} KB, used by {len(refs)} page(s), e.g. {sorted(refs)[0]}"))

    summary = {"pages": len(pages), "failures": len(fails), "warnings": len(warns),
               "atlas_frozen_skipped": 0 if args.with_atlas else skipped_atlas}
    if args.json:
        print(json.dumps({"summary": summary, "failures": fails, "warnings": warns}, indent=1, ensure_ascii=False))
    else:
        print(f"checked {len(pages)} site pages in {site}" + ("" if args.with_atlas else f" (Atlas not assembled: {skipped_atlas} frozen Atlas paths skipped)"))
        for title, rows in (("FAIL", fails), ("warn", warns)):
            for rule, where, what in rows:
                print(f"{title}  {rule:9s} {where}  {what}")
        print(f"{len(fails)} failure(s), {len(warns)} warning(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
