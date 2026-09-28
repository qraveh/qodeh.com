#!/usr/bin/env python3
"""Tell the IndexNow engines (Bing, Yandex, Seznam, Naver; not Google) which qodeh.com pages are live.

Run by .github/workflows/deploy-aws.yml after the S3 sync and the CloudFront invalidation, so every URL
it names already serves the new version. It reads the URLs from the built site's two sitemaps — Hugo's
and the Quantum Technology Atlas's — and POSTs them in one request (IndexNow takes up to 10,000).

The key is the one hosted since 24 Aug 2026 as static/<key>.txt, whose only content is the key itself;
it is found by that rule, so nothing here has to change if the key is ever rotated.

    python3 infra/indexnow.py public            # submit
    python3 infra/indexnow.py public --dry-run  # print what would be submitted

Standard library only. Exit status is 0 on 200/202 and 1 otherwise; the workflow step does not stop the
deploy on failure, because by the time it runs the site is already live.
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

HOST = "qodeh.com"
ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAPS = ["sitemap.xml", "publications/quantum-technology-atlas/sitemap.xml"]
LIMIT = 10_000


def find_key(static_dir: pathlib.Path) -> str:
    for f in sorted(static_dir.glob("*.txt")):
        if re.fullmatch(r"[0-9a-f]{8,128}", f.stem) and f.read_text(encoding="utf-8").strip() == f.stem:
            return f.stem
    sys.exit("indexnow: no key file static/<key>.txt whose content is its own name")


def urls_from(public: pathlib.Path) -> list[str]:
    seen, out = set(), []
    for rel in SITEMAPS:
        p = public / rel
        if not p.is_file():
            print(f"indexnow: {rel} not in the build, skipped")
            continue
        for u in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", p.read_text(encoding="utf-8")):
            if u.startswith(f"https://{HOST}/") and u not in seen:
                seen.add(u)
                out.append(u)
    return out


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    public = pathlib.Path(args[0] if args else "public")
    repo = pathlib.Path(__file__).resolve().parent.parent
    key = find_key(repo / "static")
    urls = urls_from(public)
    if not urls:
        print("indexnow: no URLs found")
        return 1
    if len(urls) > LIMIT:
        print(f"indexnow: {len(urls)} URLs, submitting the first {LIMIT}")
        urls = urls[:LIMIT]
    body = {"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}
    print(f"indexnow: {len(urls)} URLs from {', '.join(SITEMAPS)}")
    if dry:
        for u in urls[:5] + (["..."] if len(urls) > 10 else []) + urls[-5:]:
            print("  " + u)
        return 0
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
    except urllib.error.URLError as e:
        print(f"indexnow: request failed: {e.reason}")
        return 1
    # 200 OK and 202 Accepted are success; 403 key not valid, 422 URLs not on the host, 429 too many requests
    print(f"indexnow: HTTP {status}")
    return 0 if status in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
