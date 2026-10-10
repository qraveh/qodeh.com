"""Faithful vector redraw of the Qodeh logo from its PNG master (static/logo.png, 2432x2504, RGBA).

Method (deterministic, reproducible):
  1. Outlines: the master's edges are feathered (~3-6 px at 2432 px), so the true edge is the 50 % alpha iso-line,
     traced at sub-pixel precision with contourpy.
  2. Curves: each closed outline is split at its real corners and fitted with cubic Beziers (Schneider, "An
     Algorithm for Automatically Fitting Digitized Curves", Graphics Gems 1990), error tolerance in master pixels.
  3. Gradients: the bands and the wordmark each get a linear gradient along their measured colour direction; stops
     are medians of the master's pixels in slabs along that direction (stars excluded), reduced to the fewest stops
     that keep every slab within TOL_RGB. The wordmark gradient also carries the master's opacity ramp.
  4. Stars: points of light are detected as residual brightness over the band gradient, then drawn as soft circles
     clipped to the bands.
Output: logo-full.svg (viewBox in master pixels) and a JSON report of what was measured.
Usage: python vectorize.py <logo.png> <out-dir>
"""
import json, math, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import contourpy

FIT_ERR = 0.9          # max Bezier deviation from the traced edge, in master pixels (0.04 % of the width)
CORNER_DEG = 38        # turning angle (over a ~6 px window) that counts as a real corner
TOL_RGB = 2.0          # gradient stop reduction: max deviation per channel, 0-255
STAR_RES = 10.0        # min residual lightness over the band gradient for a pixel to belong to a star
STAR_PEAK = 18.0       # min peak residual for a star to be kept


# ------------------------------------------------------------------ Bezier fitting (Schneider)
def bez(p, t):
    mt = 1 - t
    return (mt**3)[:, None] * p[0] + (3 * mt**2 * t)[:, None] * p[1] + (3 * mt * t**2)[:, None] * p[2] + (t**3)[:, None] * p[3]


def bez_d1(p, t):
    mt = 1 - t
    return (3 * mt**2)[:, None] * (p[1] - p[0]) + (6 * mt * t)[:, None] * (p[2] - p[1]) + (3 * t**2)[:, None] * (p[3] - p[2])


def bez_d2(p, t):
    mt = 1 - t
    return (6 * mt)[:, None] * (p[2] - 2 * p[1] + p[0]) + (6 * t)[:, None] * (p[3] - 2 * p[2] + p[1])


def chord_params(pts):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    return d / d[-1] if d[-1] > 0 else np.linspace(0, 1, len(pts))


def generate(pts, u, t1, t2):
    p0, p3 = pts[0], pts[-1]
    a1, a2 = np.outer(3 * (1 - u)**2 * u, t1), np.outer(3 * (1 - u) * u**2, t2)
    c = np.array([[np.sum(a1 * a1), np.sum(a1 * a2)], [np.sum(a1 * a2), np.sum(a2 * a2)]])
    base = bez(np.array([p0, p0, p3, p3]), u)
    tmp = pts - base
    x = np.array([np.sum(a1 * tmp), np.sum(a2 * tmp)])
    det = c[0, 0] * c[1, 1] - c[0, 1] * c[1, 0]
    seg = np.linalg.norm(p3 - p0)
    if abs(det) > 1e-12:
        al1 = (x[0] * c[1, 1] - x[1] * c[0, 1]) / det
        al2 = (c[0, 0] * x[1] - c[1, 0] * x[0]) / det
    else:
        al1 = al2 = seg / 3
    eps = 1e-6 * seg
    if al1 < eps or al2 < eps:
        al1 = al2 = seg / 3
    return np.array([p0, p0 + t1 * al1, p3 + t2 * al2, p3])


def reparam(p, pts, u):
    q, q1, q2 = bez(p, u), bez_d1(p, u), bez_d2(p, u)
    num = np.sum((q - pts) * q1, axis=1)
    den = np.sum(q1 * q1, axis=1) + np.sum((q - pts) * q2, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        nu = np.where(np.abs(den) > 1e-12, u - num / den, u)
    return np.clip(nu, 0, 1)


def max_err(p, pts, u):
    d = np.linalg.norm(bez(p, u) - pts, axis=1)
    i = int(np.argmax(d))
    return d[i], i


def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def fit_cubic(pts, t1, t2, err, out, depth=0):
    if len(pts) == 2:
        dist = np.linalg.norm(pts[1] - pts[0]) / 3
        out.append(np.array([pts[0], pts[0] + t1 * dist, pts[1] + t2 * dist, pts[1]]))
        return
    u = chord_params(pts)
    p = generate(pts, u, t1, t2)
    e, split = max_err(p, pts, u)
    if e < err:
        out.append(p); return
    if e < err * 4:
        for _ in range(24):
            u = reparam(p, pts, u)
            p = generate(pts, u, t1, t2)
            e, split = max_err(p, pts, u)
            if e < err:
                out.append(p); return
    split = min(max(split, 1), len(pts) - 2)
    tc = unit(pts[split - 1] - pts[split + 1])
    fit_cubic(pts[:split + 1], t1, tc, err, out, depth + 1)
    fit_cubic(pts[split:], -tc, t2, err, out, depth + 1)


def resample(poly, step=1.0):
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(poly, axis=0), axis=1))]
    n = max(int(d[-1] / step), 8)
    s = np.linspace(0, d[-1], n)
    return np.c_[np.interp(s, d, poly[:, 0]), np.interp(s, d, poly[:, 1])]


def corners(closed):
    """Indices of real corners on a closed, uniformly resampled outline."""
    n, w = len(closed), 6
    ang = np.zeros(n)
    for i in range(n):
        a, b = closed[(i - w) % n] - closed[i], closed[(i + w) % n] - closed[i]
        cosv = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12)
        ang[i] = 180 - math.degrees(math.acos(max(-1, min(1, cosv))))
    idx = [i for i in range(n) if ang[i] > CORNER_DEG and ang[i] == max(ang[(i + k) % n] for k in range(-w, w + 1))]
    return idx


def smooth(pts, cs, half=2):
    """Moving average over 2*half+1 points, leaving a margin of points around each corner untouched."""
    n = len(pts)
    near = np.zeros(n, bool)
    for c in cs:
        for j in range(-6, 7):
            near[(c + j) % n] = True
    out = pts.copy()
    for i in range(n):
        if not near[i]:
            out[i] = pts[[(i + j) % n for j in range(-half, half + 1)]].mean(axis=0)
    return out


def sharpen(pts, cs, k1=4, k2=18, reach=6.0):
    """Feathering rounds a sharp corner; rebuild it where the two adjacent edges' tangent lines meet."""
    n = len(pts)
    out = pts.copy()
    for c in cs:
        A = pts[[(c - j) % n for j in range(k1, k2)]]
        B = pts[[(c + j) % n for j in range(k1, k2)]]
        da, db = unit(A[0] - A[-1]), unit(B[0] - B[-1])
        ca, cb = A.mean(axis=0), B.mean(axis=0)
        m = np.array([da, -db]).T
        if abs(np.linalg.det(m)) < 0.15:      # nearly parallel: not a corner that lines can rebuild
            continue
        t = np.linalg.solve(m, cb - ca)
        P = ca + t[0] * da
        if np.linalg.norm(P - pts[c]) > reach:
            continue
        a0, b0 = pts[(c - k1) % n], pts[(c + k1) % n]
        for j in range(1, k1):
            out[(c - j) % n] = a0 + (P - a0) * (k1 - j) / k1
            out[(c + j) % n] = b0 + (P - b0) * (k1 - j) / k1
        out[c] = P
    return out


def fit_closed(poly, err):
    pts = resample(poly + 0.5, 1.0)  # array index i is the centre of SVG pixel [i, i+1]: shift by half a pixel
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    cs = corners(pts)
    segs = []
    if not cs:  # smooth loop: start at the lowest point, treat as open with matching tangents
        k = int(np.argmax(pts[:, 1]))
        pts = np.roll(pts, -k, axis=0)
        pts = np.vstack([pts, pts[:1]])
        t = unit(pts[1] - pts[-2])
        fit_cubic(pts, t, -t, err, segs)
        return segs, 0
    pts = sharpen(smooth(pts, cs), cs)
    pts = np.roll(pts, -cs[0], axis=0)
    cs = [(c - cs[0]) % len(pts) for c in cs] + [len(pts)]
    loop = np.vstack([pts, pts[:1]])
    for a, b in zip(cs[:-1], cs[1:]):
        piece = loop[a:b + 1]
        if len(piece) < 2:
            continue
        k = min(3, len(piece) - 1)
        fit_cubic(piece, unit(piece[k] - piece[0]), unit(piece[-1 - k] - piece[-1]), err, segs)
    return segs, len(cs) - 1


def path_d(segs_list):
    f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
    out = []
    for segs in segs_list:
        p0 = segs[0][0]
        s = [f"M{f(p0[0])} {f(p0[1])}"]
        for p in segs:
            chord = p[3] - p[0]
            ln = np.linalg.norm(chord)
            dev = 0 if ln < 1e-9 else max(abs(np.cross(chord, p[1] - p[0])), abs(np.cross(chord, p[2] - p[0]))) / ln
            if dev < 0.3:
                s.append(f"L{f(p[3][0])} {f(p[3][1])}")
            else:
                s.append(f"C{f(p[1][0])} {f(p[1][1])} {f(p[2][0])} {f(p[2][1])} {f(p[3][0])} {f(p[3][1])}")
        out.append("".join(s) + "Z")
    return "".join(out)


# ------------------------------------------------------------------ gradients
def direction(rgb, mask):
    ys, xs = np.nonzero(mask)
    X = np.c_[xs, ys, np.ones_like(xs)]
    lum = rgb[mask] @ np.array([0.2126, 0.7152, 0.0722])
    c, *_ = np.linalg.lstsq(X, lum, rcond=None)
    return unit(np.array([c[0], c[1]]))


def gradient_stops(rgb, alpha, mask, dvec, slab=6, with_alpha=False, exclude=None):
    ys, xs = np.nonzero(mask)
    proj = xs * dvec[0] + ys * dvec[1]
    lo, hi = proj.min(), proj.max()
    keep = np.ones(len(xs), bool) if exclude is None else ~exclude[ys, xs]
    bins = np.arange(lo, hi + slab, slab)
    idx = np.clip(np.digitize(proj, bins) - 1, 0, len(bins) - 2)
    rows = []
    for b in range(len(bins) - 1):
        sel = (idx == b) & keep
        if sel.sum() < 30:
            continue
        col = np.median(rgb[ys[sel], xs[sel]], axis=0)
        al = np.median(alpha[ys[sel], xs[sel]]) if with_alpha else 255.0
        rows.append(((bins[b] + slab / 2 - lo) / (hi - lo), *col, al))
    rows = np.array(rows)
    # greedy reduction: keep the fewest stops whose linear interpolation stays within TOL_RGB of every slab
    keepi = [0]
    i = 0
    while i < len(rows) - 1:
        j = len(rows) - 1
        while j > i + 1:
            t = (rows[i + 1:j, 0] - rows[i, 0]) / (rows[j, 0] - rows[i, 0])
            interp = rows[i, 1:] + t[:, None] * (rows[j, 1:] - rows[i, 1:])
            if np.abs(interp - rows[i + 1:j, 1:]).max() <= TOL_RGB:
                break
            j -= 1
        keepi.append(j)
        i = j
    stops = rows[keepi]
    p1 = np.array([0, 0]) + 0
    # gradient line endpoints in user space: from the min projection to the max projection, through the mask centre
    cy, cx = ys.mean(), xs.mean()
    c_proj = cx * dvec[0] + cy * dvec[1]
    start = np.array([cx, cy]) + (lo - c_proj) * dvec + 0.5   # pixel centres → SVG coordinates
    end = np.array([cx, cy]) + (hi - c_proj) * dvec + 0.5
    return stops, start, end, rows


def stop_xml(stops, with_alpha):
    out = []
    for s in stops:
        col = "#%02x%02x%02x" % tuple(int(round(min(255, max(0, v)))) for v in s[1:4])
        op = f' stop-opacity="{s[4] / 255:.3f}"' if with_alpha and s[4] < 254.5 else ""
        out.append(f'<stop offset="{s[0]:.4f}" stop-color="{col}"{op}/>')
    return "".join(out)


# ------------------------------------------------------------------ main
def main():
    src, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    im = np.asarray(Image.open(src).convert("RGBA")).astype(np.float64)
    H, W = im.shape[:2]
    rgb, a = im[..., :3], im[..., 3]
    solid = a > 127.5
    lab, n = ndi.label(solid)
    comps = sorted(range(1, n + 1), key=lambda k: (ndi.find_objects(lab)[k - 1][0].start, ndi.find_objects(lab)[k - 1][1].start))
    sizes = {k: int((lab == k).sum()) for k in comps}
    bands = [k for k in comps if ndi.find_objects(lab)[k - 1][0].start < 200 and sizes[k] > 100000]
    letters = [k for k in comps if k not in bands and sizes[k] > 20000]

    # outlines at the 50 % alpha line
    gen = contourpy.contour_generator(z=a, line_type=contourpy.LineType.Separate)
    lines = [l for l in gen.lines(127.5) if len(l) > 40]
    def owner(line):
        c = line.mean(axis=0)
        # a hole's centroid lies outside the solid: take the component that encloses it via nearest solid pixel
        y, x = int(round(c[1])), int(round(c[0]))
        k = lab[min(max(y, 0), H - 1), min(max(x, 0), W - 1)]
        if k == 0:
            pts = line[:: max(1, len(line) // 50)]
            ks = [lab[min(max(int(round(p[1])) + dy, 0), H - 1), min(max(int(round(p[0])) + dx, 0), W - 1)]
                  for p in pts for dy in (-2, 0, 2) for dx in (-2, 0, 2)]
            ks = [q for q in ks if q]
            k = max(set(ks), key=ks.count) if ks else 0
        return k
    groups = {"bands": [], "word": {}}
    stats = {"outlines": 0, "segments": 0, "corners": 0}
    for l in lines:
        k = owner(l)
        if k in bands or k in letters:
            segs, nc = fit_closed(l, FIT_ERR)
            (groups["bands"].append(segs) if k in bands else groups["word"].setdefault(k, []).append(segs))
            stats["outlines"] += 1; stats["segments"] += len(segs); stats["corners"] += nc

    core = solid & (ndi.distance_transform_edt(solid) > 6)
    bmask = core & np.isin(lab, bands)
    wmask = core & np.isin(lab, letters)

    # band gradient (stars excluded by a first pass)
    dvb = direction(rgb, bmask)
    stops_b, sb, eb, rows_b = gradient_stops(rgb, a, bmask, dvb)
    ys, xs = np.nonzero(solid & np.isin(lab, bands))
    pr = ((xs * dvb[0] + ys * dvb[1]) - (xs * dvb[0] + ys * dvb[1]).min())
    pr = pr / pr.max()
    lum = lambda c: c @ np.array([0.2126, 0.7152, 0.0722])
    model = np.c_[[np.interp(pr, rows_b[:, 0], rows_b[:, ch]) for ch in (1, 2, 3)]].T
    resid = np.zeros((H, W))
    resid[ys, xs] = lum(rgb[ys, xs]) - lum(model)
    starpix = resid > STAR_RES
    stops_b, sb, eb, rows_b = gradient_stops(rgb, a, bmask, dvb, exclude=ndi.binary_dilation(starpix, iterations=2))

    letter_grads = {}
    for k in letters:
        lm = core & (lab == k)
        dvk = direction(rgb, lm)
        st, s0, e0, _ = gradient_stops(rgb, a, lm, dvk, slab=5, with_alpha=True)
        letter_grads[k] = (st, s0, e0, dvk)

    # stars
    sl, sn = ndi.label(starpix, structure=np.ones((3, 3)))
    stars = []
    for k, obj in enumerate(ndi.find_objects(sl), 1):
        m = sl[obj] == k
        r = resid[obj] * m
        peak = r.max()
        if peak < STAR_PEAK:
            continue
        yy, xx = np.nonzero(m)
        area = int(m.sum())
        wts = r[m]
        cy = obj[0].start + (yy * wts).sum() / wts.sum()
        cx = obj[1].start + (xx * wts).sum() / wts.sum()
        var = (((yy + obj[0].start - cy) ** 2 + (xx + obj[1].start - cx) ** 2) * wts).sum() / wts.sum() / 2
        sigma = max(0.6, math.sqrt(var)) * 1.15
        loc = rgb[obj][m]
        top = loc[np.argmax(r[m])]
        base_l = lum(top) - peak
        opac = float(np.clip(peak / max(1.0, 255 - base_l), 0.1, 1.0))
        core_r = math.sqrt(max(1, (r[m] > 0.5 * peak).sum()) / math.pi)
        full_r = math.sqrt(area / math.pi)
        frac = core_r / max(full_r, 1e-6)
        cls = 0 if (frac < 0.38 or area < 8) else (1 if frac < 0.62 else 2)
        rad = max(1.0, full_r * 0.92)
        stars.append((cx + 0.5, cy + 0.5, rad, opac, cls))

    f = lambda v: f"{v:.1f}".rstrip("0").rstrip(".")
    d_b = path_d(groups["bands"])
    star_xml = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="url(#qs{c})" fill-opacity="{o:.2f}"/>' for x, y, r, o, c in stars)
    def prof(cf):
        return (f'<stop offset="0" stop-color="#fff"/><stop offset="{cf:.2f}" stop-color="#fff" stop-opacity=".95"/>'
                f'<stop offset="{(cf + 1) / 2:.2f}" stop-color="#fff" stop-opacity=".4"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>')
    star_defs = "".join(f'<radialGradient id="qs{i}">{prof(cf)}</radialGradient>' for i, cf in enumerate((0.1, 0.32, 0.58)))
    defs = [f'<linearGradient id="qb" gradientUnits="userSpaceOnUse" x1="{f(sb[0])}" y1="{f(sb[1])}" x2="{f(eb[0])}" y2="{f(eb[1])}">{stop_xml(stops_b, False)}</linearGradient>',
            star_defs, f'<clipPath id="qc"><path d="{d_b}"/></clipPath>']
    letters_xml = []
    for i, k in enumerate(sorted(letter_grads, key=lambda k: ndi.find_objects(lab)[k - 1][1].start)):
        st, s0, e0, _ = letter_grads[k]
        defs.append(f'<linearGradient id="q{i}" gradientUnits="userSpaceOnUse" x1="{f(s0[0])}" y1="{f(s0[1])}" x2="{f(e0[0])}" y2="{f(e0[1])}">{stop_xml(st, True)}</linearGradient>')
        letters_xml.append(f'<path fill="url(#q{i})" fill-rule="evenodd" d="{path_d(groups["word"].get(k, []))}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="Qodeh"><defs>{"".join(defs)}</defs>'
           f'<path fill="url(#qb)" d="{d_b}"/><g clip-path="url(#qc)">{star_xml}</g>{"".join(letters_xml)}</svg>')
    open(os.path.join(outdir, "logo-full.svg"), "w", encoding="utf-8", newline="\n").write(svg)
    rep = dict(source=src, size=[W, H], bands=len(bands), letters=len(letters), **stats,
               band_direction=dvb.round(4).tolist(), band_stops=len(stops_b), letter_stops=[len(v[0]) for v in letter_grads.values()],
               stars=len(stars), svg_bytes=len(svg.encode()), params=dict(FIT_ERR=FIT_ERR, CORNER_DEG=CORNER_DEG, TOL_RGB=TOL_RGB, STAR_RES=STAR_RES, STAR_PEAK=STAR_PEAK))
    json.dump(rep, open(os.path.join(outdir, "report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
