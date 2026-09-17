# -*- coding: utf-8 -*-
r"""Open Graph card for the Superconductor Electronics Monitor 2026 publication page.

Composition and palette are lifted from the edition's own cover slide, so a reader
who meets the card in a feed and then opens the PDF meets the same object: navy
ground #13203c, a darker right rail #0d172f carrying the Qodeh mark and a gold
2026, white Calibri Bold title, #d9e4f5 subtitle, #8fa8ce meta. Calibri and not
the site's Segoe UI on purpose — the card depicts the publication, and the
publication's face is Calibri.

qodeh-mark.png is the deck's own ppt/media/image1.png, extracted from the
pptx rather than redrawn.

Re-run per edition, changing the eyebrow, then drop the result in
assets/images/ — layouts/partials/templates/opengraph.html reads its real
width and height from there, so the meta tags follow the file.

Rendered at 3x and downsampled: Pillow places glyphs on whole pixels, and at 1x
the letter-spaced eyebrow goes ragged.

    python make_og.py [out.png]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent

W, H, S = 1200, 627, 3
NAVY, RAIL_C, HAIR = "#13203c", "#0d172f", "#1b2a4a"
WHITE, SUB, MUTED, GOLD, RULE = "#ffffff", "#d9e4f5", "#8fa8ce", "#c8951f", "#24345a"
FD = r"C:\Windows\Fonts"
BOLD, REG = FD + r"\calibrib.ttf", FD + r"\calibri.ttf"
f = lambda p, s: ImageFont.truetype(p, s * S)

RAIL_X = int(W * 0.8215)          # the cover's own split
X      = 64                       # text column
GUTTER = 46                       # keep every rule and glyph this far off the rail

im = Image.new("RGB", (W * S, H * S), NAVY)
d  = ImageDraw.Draw(im)
d.rectangle([RAIL_X * S, 0, W * S, H * S], fill=RAIL_C)
d.line([(RAIL_X * S, 0), (RAIL_X * S, H * S)], fill=HAIR, width=S)

logo = Image.open(HERE / "qodeh-mark.png").convert("RGBA")
lw = int((W - RAIL_X) * 0.62)
lh = int(lw * logo.height / logo.width)
lg = logo.resize((lw * S, lh * S), Image.LANCZOS)
im.paste(lg, ((RAIL_X + (W - RAIL_X - lw) // 2) * S, 46 * S), lg)

def tracked(xy, text, font, fill, track):
    x, y = xy[0] * S, xy[1] * S
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + track * S

tracked((X, 116), "V1.1  ·  6 SEPTEMBER 2026  ·  CC BY 4.0", f(REG, 19), MUTED, 2.4)
d.rectangle([X * S, 158 * S, (X + 54) * S, 161 * S], fill=GOLD)     # borrows the cover's only gold

title, t = ["Superconductor Electronics", "Monitor 2026"], f(BOLD, 68)
for i, line in enumerate(title):
    w = d.textlength(line, font=t) / S
    assert X + w < RAIL_X - GUTTER, f"title line {i} is {X + w:.0f}px wide, rail starts at {RAIL_X}"
    d.text((X * S, (192 + i * 80) * S), line, font=t, fill=WHITE)

d.text((X * S, 376 * S), "Markets, money, maturity, technology comparison",
       font=f(REG, 27), fill=SUB)

d.line([(X * S, 468 * S), ((RAIL_X - GUTTER) * S, 468 * S)], fill=RULE, width=S)
name, fn = "Raveh Neeman", f(BOLD, 24)
d.text((X * S, 494 * S), name, font=fn, fill=WHITE)
d.text(((X + d.textlength(name, font=fn) / S + 14) * S, 495 * S),
       "·  Qodeh  ·  qodeh.com", font=f(REG, 23), fill=MUTED)

y2 = f(BOLD, 34)
d.text(((RAIL_X + (W - RAIL_X - d.textlength("2026", font=y2) / S) / 2) * S, 540 * S),
       "2026", font=y2, fill=GOLD)

out = sys.argv[1] if len(sys.argv) > 1 else str(
    HERE.parent.parent / "assets" / "images" /
    "superconductor-electronics-monitor-2026-social.png")
im.resize((W, H), Image.LANCZOS).save(out, optimize=True)
print("wrote", out)
