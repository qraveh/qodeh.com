"""Render logo-full.svg with headless Edge and compare it with the PNG master, on white and on black.

Usage: python compare.py <logo.png> <logo-full.svg> <work-dir> <edge.exe>
Writes: render-white.png, render-black.png, diff-white.png (amplified), metrics.json, and side-by-side
strips at 32, 200 and 1200 px wide (master left, vector right) for the editor's eye.
"""
import json, os, subprocess, sys, time
import numpy as np
from PIL import Image


def render(svg, out_png, w, h, bg, edge, work):
    page = os.path.join(work, f"r-{bg.strip('#')}-{w}.html")
    svg_url = "file:///" + os.path.abspath(svg).replace("\\", "/")
    open(page, "w", encoding="utf-8").write(
        f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:{bg}}}img{{display:block;width:{w}px;height:{h}px}}</style></head>'
        f'<body><img src="{svg_url}"></body></html>')
    prof = os.path.join(work, "edge-prof")
    if os.path.exists(out_png):
        os.remove(out_png)
    for _ in range(3):
        subprocess.run([edge, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={prof}",
                        "--allow-file-access-from-files", "--force-device-scale-factor=1", "--virtual-time-budget=8000",
                        f"--window-size={max(w, 600)},{h + 100}", f"--screenshot={out_png}", "file:///" + page.replace("\\", "/")],
                       capture_output=True, timeout=180)
        for _ in range(20):
            if os.path.exists(out_png) and os.path.getsize(out_png) > 0:
                break
            time.sleep(0.5)
        if os.path.exists(out_png):
            break
    return np.asarray(Image.open(out_png).convert("RGB"))[:h, :w].astype(np.float64)


def flatten(png, bg_rgb, size=None):
    im = Image.open(png).convert("RGBA")
    if size:
        im = im.resize(size, Image.LANCZOS)
    base = Image.new("RGBA", im.size, bg_rgb + (255,))
    base.alpha_composite(im)
    return np.asarray(base.convert("RGB")).astype(np.float64)


def main():
    png, svg, work, edge = sys.argv[1:5]
    os.makedirs(work, exist_ok=True)
    W, H = Image.open(png).size
    metrics = {}
    for name, bg, rgbv in (("white", "#ffffff", (255, 255, 255)), ("black", "#000000", (0, 0, 0))):
        r = render(svg, os.path.join(work, f"render-{name}.png"), W, H, bg, edge, work)
        m = flatten(png, rgbv)
        d = np.abs(r - m)
        mse = (d ** 2).mean()
        ink = (np.abs(m - np.array(rgbv)).sum(axis=2) > 30) | (np.abs(r - np.array(rgbv)).sum(axis=2) > 30)
        dm = d.max(axis=2)
        metrics[name] = dict(psnr_db=round(10 * np.log10(255 ** 2 / mse), 2) if mse > 0 else 99,
                             mean_abs_err=round(float(d.mean()), 3),
                             mean_abs_err_on_ink=round(float(d[ink].mean()), 3),
                             share_ink_pixels_err_gt_24=round(float((dm[ink] > 24).mean()), 4),
                             share_ink_pixels_err_gt_48=round(float((dm[ink] > 48).mean()), 4))
        if name == "white":
            Image.fromarray(np.clip(dm * 4, 0, 255).astype(np.uint8)).save(os.path.join(work, "diff-white.png"))
    # side-by-side strips at display sizes (master downscaled with LANCZOS vs vector rendered at that size)
    for w in (32, 200, 1200):
        h = round(H * w / W)
        r = render(svg, os.path.join(work, f"v{w}.png"), w, h, "#ffffff", edge, work).astype(np.uint8)
        m = flatten(png, (255, 255, 255), (w, h)).astype(np.uint8)
        gap = max(8, w // 10)
        strip = Image.new("RGB", (w * 2 + gap, h), (200, 200, 200))
        strip.paste(Image.fromarray(m), (0, 0)); strip.paste(Image.fromarray(r), (w + gap, 0))
        strip.save(os.path.join(work, f"side-{w}.png"))
    json.dump(metrics, open(os.path.join(work, "metrics.json"), "w"), indent=1)
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
