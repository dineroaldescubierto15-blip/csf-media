#!/usr/bin/env python3
"""Ilustraciones realistas a partir de fotos con licencia libre (para cuando una foto no queda bien en un Reel).

La ilustración se hace SOBRE la foto real (no se inventa la cara): recorta a la persona, la pinta con un acabado de
ilustración y la coloca sobre el fondo de la marca. Así la cara es la de la foto, pero con estética propia.

Uso:
  python3 tools/ilustrar.py candidatos "<persona>" <carpeta> [--n 15] [--fuentes commons,openverse,unsplash]
      -> descarga las N mejores fotos con licencia libre (Commons, Openverse/Flickr, Unsplash) a <carpeta>/cand_NN.jpg,
         hoja de contacto <carpeta>/candidatos.jpg y lista con autor/licencia/tamaño en <carpeta>/candidatos.json
  python3 tools/ilustrar.py hacer <foto.jpg> <carpeta> [--credito "Foto: X / Wikimedia Commons, CC BY-SA 2.0"]
      -> <carpeta>/ilus_pintura.jpg, ilus_editorial.jpg, ilus_duotono.jpg (1080x1350) + recorte transparente .png
  python3 tools/ilustrar.py recorte <foto.jpg> <carpeta> [--cerca]
      -> solo quita el fondo y pasa la foto a la paleta del perfil: rec_paleta, rec_bn, rec_calido, rec_original
  python3 tools/ilustrar.py dibujo <foto.jpg> <carpeta> [--cerca]   (--cerca: primer plano de cabeza y hombros)
      -> estilos de dibujo (menos realistas): dib_comic, dib_poster, dib_lapiz, dib_trama, dib_linea, dib_acuarela
Necesita: opencv-contrib-python-headless<5 (óleo con xphoto), rembg[cpu] (recorte de la persona), pillow, numpy.
Crédito: "Ilustración: Capital Sin Filtros, a partir de una foto de <autor> (Wikimedia Commons, <licencia>)".
Si la foto es CC BY-SA, la ilustración se comparte con la misma licencia. Nunca se cambia la expresión ni se
añade nada que la persona no haya hecho: es la misma foto, ilustrada.
"""
import json, sys, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
W, H = 1080, 1350
CERCA = '--cerca' in sys.argv    # primer plano (cabeza y hombros)
GOLD = np.array([66, 197, 244], np.float32)   # BGR de #F4C542
BG = np.array([10, 10, 10], np.float32)

def candidatos(persona, out, n=15, fuentes=None):
    """Busca en varias fuentes con licencia libre: Wikimedia Commons, Openverse (sobre todo Flickr) y Unsplash."""
    import assets, cv2, os
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    # Unsplash no sirve para personas concretas (devuelve gente cualquiera): solo Commons y Openverse
    fuentes = fuentes or ["commons", "openverse"]
    cs = []
    consultas = [persona, f"{persona} portrait", f"{persona} keynote", f"{persona} 2025", f"{persona} 2024", f"{persona} interview"]
    for f in fuentes:
        for q in (consultas if f == "commons" else consultas[:2]):
            try:
                got = assets.search(f, q, 20)
                for c in got: c["de"] = f
                cs += got; print(f"{f} «{q}»: {len(got)} resultados")
            except BaseException as e:
                print(f"{f} «{q}»: error {e}")
    seen = set(); uniq = []
    for c in cs:
        k = (c.get("autor"), c.get("w"), c.get("h"))
        if k in seen: continue
        seen.add(k); uniq.append(c)
    uniq = [c for c in uniq if (c.get("w") or 1000) >= 800 and (c.get("h") or 1000) >= 800]
    uniq = sorted(uniq, key=lambda c: -((c.get("w") or 1000) * (c.get("h") or 1000)))
    por_autor = {}; div = []                      # variedad: como mucho 3 fotos del mismo autor
    for c in uniq:
        k = str(c.get("autor")).lower()[:20]; por_autor[k] = por_autor.get(k, 0) + 1
        if por_autor[k] <= 3: div.append(c)
    uniq = div[:n]
    lst = []
    for i, c in enumerate(uniq, 1):
        f = out / f"cand_{i:02d}.jpg"
        try: f.write_bytes(assets.get(c["url"]))
        except Exception as e: print(f"  no se pudo bajar {c['url']}: {e}"); continue
        lst.append({"n": i, "archivo": f.name, "de": c["de"], **{k: c.get(k) for k in ("id", "autor", "licencia", "w", "h", "pagina", "desc", "credito")}})
        print(f"{i}. [{c['de']}] {c['licencia']} · {c.get('w')}x{c.get('h')} · {str(c['autor'])[:40]} · {str(c.get('desc'))[:50]}")
    (out / "candidatos.json").write_text(json.dumps(lst, ensure_ascii=False, indent=1), encoding="utf-8")
    th = []
    for c in lst:
        im = cv2.imread(str(out / c["archivo"]))
        if im is None: continue
        s_ = 320 / max(im.shape[:2]); im = cv2.resize(im, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA)
        cell = np.full((360, 320, 3), 10, np.uint8); y = (320 - im.shape[0]) // 2; x = (320 - im.shape[1]) // 2
        cell[y:y + im.shape[0], x:x + im.shape[1]] = im
        cv2.putText(cell, f"{c['n']} {c['de'][:9]}", (8, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (66, 197, 244), 2)
        th.append(cell)
    cols = 5; rows = max(1, (len(th) + cols - 1) // cols)
    sheet = np.full((rows * 360, cols * 320, 3), 10, np.uint8)
    for i, t in enumerate(th): sheet[(i // cols) * 360:(i // cols) * 360 + 360, (i % cols) * 320:(i % cols) * 320 + 320] = t
    cv2.imwrite(str(out / "candidatos.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88])

def _cutout(img):
    from rembg import remove, new_session
    import cv2
    rgba = remove(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), session=new_session("u2net_human_seg"), post_process_mask=True)
    a = rgba[..., 3].astype(np.float32) / 255
    return a

def _frame(img, a):
    """Encuadre de busto: margen sobre la cabeza (~9 %), la persona centrada y llenando el ancho."""
    import cv2
    ys, xs = np.nonzero(a > 0.5)
    top, bot = ys.min(), ys.max(); left, right = np.percentile(xs, 2), np.percentile(xs, 98)
    cx = (left + right) / 2
    head = np.nonzero(a[top:top + max(10, (bot - top) // 4)] > 0.5)[1]
    if len(head): cx = 0.5 * cx + 0.5 * head.mean()        # centra entre el cuerpo y la cabeza
    side_h = (bot - top) / 0.91                            # la persona ocupa desde el 9 % hasta abajo
    rows = (a > 0.5).sum(axis=1).astype(np.float32); hw = np.median(rows[top:top + max(5, (bot - top) // 10)])
    head_h = next((i for i in range(top, bot) if rows[i] > 2.2 * max(hw, 1)), bot) - top   # hasta los hombros
    if CERCA and head_h > 0:
        side_h = min(side_h, head_h * 2.3)                 # primer plano: cabeza y hombros
    if not CERCA:
        side_h = min(side_h, (right - left) * 1.15 * H / W)    # que quepan los hombros
    side_w = side_h * W / H
    x0, y0 = cx - side_w / 2, top - side_h * 0.09
    M = np.float32([[W / side_w, 0, -x0 * W / side_w], [0, H / side_h, -y0 * H / side_h]])
    im2 = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    a2 = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    # si la foto acaba antes que el lienzo, funde la parte de abajo hacia el fondo
    yb = int(min(H, (img.shape[0] - y0) * H / side_h))
    if yb < H:
        fade = np.ones(H, np.float32); n = min(160, yb); fade[yb - n:yb] = np.linspace(1, 0, n); fade[yb:] = 0
        a2 *= fade[:, None]
    return im2, a2

def _background(kind="glow"):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W * 0.5) / (W * 0.62)) ** 2 + ((yy - H * 0.38) / (H * 0.55)) ** 2)
    glow = np.clip(1 - d, 0, 1) ** 2
    bg = BG + (GOLD - BG) * (glow[..., None] * (0.22 if kind == "glow" else 0.35))
    return bg

def _rim(a, strength=0.9):
    import cv2
    a8 = (a * 255).astype(np.uint8)
    edge = cv2.subtract(a8, cv2.erode(a8, np.ones((9, 9), np.uint8)))
    edge = cv2.GaussianBlur(edge.astype(np.float32) / 255, (0, 0), 6)
    return np.clip(edge * strength, 0, 1)

def _comp(paint, a, bg, rim=0.8):
    a3 = a[..., None]
    out = bg * (1 - a3) + paint * a3
    r = _rim(a, rim)[..., None]
    out = out * (1 - r * 0.6) + GOLD * (r * 0.6)
    return np.clip(out, 0, 255).astype(np.uint8)

def _grade(x, warm=0.10, contrast=1.12, sat=0.9):
    import cv2
    f = x.astype(np.float32) / 255
    f = np.clip((f - 0.5) * contrast + 0.5, 0, 1)
    hsv = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] *= sat; f = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255
    lum = f.mean(axis=2, keepdims=True)
    f = f * (1 - warm * lum) + (GOLD / 255) * (warm * lum)          # luces cálidas
    return f * 255

def _lines(img, amount=0.35):
    import cv2
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = 255 - g; bl = cv2.GaussianBlur(inv, (0, 0), 3)
    sketch = cv2.divide(g, 255 - bl, scale=256).astype(np.float32) / 255     # "dodge": trazo de lápiz
    return 1 - amount * (1 - np.clip(sketch, 0, 1))

def _quant(img, k=14):
    import cv2
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, lab_l, cen = cv2.kmeans(lab[::7], k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
    d = ((lab[:, None, :] - cen[None]) ** 2).sum(-1); q = cen[d.argmin(1)].reshape(img.shape).astype(np.uint8)
    return cv2.cvtColor(q, cv2.COLOR_LAB2BGR)

def hacer(foto, out, credito=None):
    import cv2
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(foto))
    a = _cutout(img)
    im, a = _frame(img, a)
    cv2.imwrite(str(out / "recorte.png"), np.dstack([im, (a * 255).astype(np.uint8)]))
    # 1) pintura realista: óleo (xphoto) sobre una base suavizada que conserva bordes, con detalle en la cara
    base = cv2.bilateralFilter(im, 7, 30, 7)
    try:
        oil = cv2.xphoto.oilPainting(base, 4, 1).astype(np.float32)
    except AttributeError:
        oil = cv2.stylization(base, sigma_s=20, sigma_r=0.25).astype(np.float32)
    det = cv2.detailEnhance(base, sigma_s=5, sigma_r=0.08).astype(np.float32)
    paint = 0.5 * cv2.GaussianBlur(oil, (0, 0), 0.8) + 0.5 * det
    blur = cv2.GaussianBlur(paint, (0, 0), 2.0); paint = cv2.addWeighted(paint, 1.35, blur, -0.35, 0)   # nitidez
    paint = _grade(np.clip(paint, 0, 255).astype(np.uint8), warm=0.12, contrast=1.1, sat=0.92) * _lines(im, 0.18)[..., None]
    cv2.imwrite(str(out / "ilus_pintura.jpg"), _comp(paint, a, _background()), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 2) editorial: manchas de color planas + línea de tinta
    q = _quant(cv2.bilateralFilter(im, 9, 60, 9), 16)
    ed = cv2.GaussianBlur(q, (0, 0), 1.2).astype(np.float32)
    ed = _grade(ed.astype(np.uint8), warm=0.14, contrast=1.15, sat=0.85) * _lines(im, 0.45)[..., None]
    cv2.imwrite(str(out / "ilus_editorial.jpg"), _comp(ed, a, _background()), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 3) duotono de marca: negro -> dorado, con trazo
    g = cv2.cvtColor(cv2.bilateralFilter(im, 9, 50, 9), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g = np.clip((g - 0.08) / 0.85, 0, 1) ** 0.9
    duo = (BG[None, None] * (1 - g[..., None]) + np.array([200, 235, 245], np.float32) * g[..., None])
    duo = duo * (1 - 0.35 * (1 - g[..., None]) * 0) * _lines(im, 0.4)[..., None]
    cv2.imwrite(str(out / "ilus_duotono.jpg"), _comp(duo, a, _background("strong"), 1.0), [cv2.IMWRITE_JPEG_QUALITY, 92])
    if credito:
        (out / "credito.txt").write_text(credito, encoding="utf-8")
    print(f"OK {out}/ilus_pintura.jpg, ilus_editorial.jpg, ilus_duotono.jpg")

# ---------- estilos de dibujo (menos realistas) ----------
def _xdog(im, sigma=0.9, k=1.6, tau=0.985, eps=0.02, phi=60):
    """Líneas de dibujo (XDoG): 1 = papel, 0 = trazo."""
    import cv2
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    g1 = cv2.GaussianBlur(g, (0, 0), sigma); g2 = cv2.GaussianBlur(g, (0, 0), sigma * k)
    d = g1 - tau * g2
    e = np.where(d >= eps, 1.0, 1 + np.tanh(phi * (d - eps)))
    return np.clip(e, 0, 1).astype(np.float32)

def _hex(h):
    h = h.lstrip("#"); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)

def _bands(im, cuts, cols, smooth=9):
    import cv2
    g = cv2.cvtColor(cv2.bilateralFilter(im, 9, 60, 9), cv2.COLOR_BGR2GRAY)
    g = cv2.medianBlur(g, smooth).astype(np.float32) / 255
    g = np.clip((g - np.percentile(g, 2)) / (np.percentile(g, 98) - np.percentile(g, 2) + 1e-6), 0, 1)
    out = np.zeros(im.shape, np.float32); idx = np.digitize(g, cuts)
    for i, c in enumerate(cols): out[idx == i] = _hex(c)
    return out

def estilos_dibujo(im, a, out):
    import cv2
    bg = _background()
    # 1) cómic: colores planos y vivos con contorno negro limpio
    sm = cv2.bilateralFilter(cv2.bilateralFilter(im, 9, 60, 9), 9, 60, 9)
    flat = _quant(cv2.pyrMeanShiftFiltering(sm, 18, 40), 8)
    flat = _grade(flat, warm=0.06, contrast=1.12, sat=1.1)
    flat = flat * 1.08
    ed = cv2.Canny(cv2.GaussianBlur(sm, (0, 0), 1.6), 40, 110)
    ed = cv2.dilate(ed, np.ones((2, 2), np.uint8)); ed = cv2.GaussianBlur(ed.astype(np.float32) / 255, (0, 0), 0.8)
    comic = flat * (1 - 0.9 * ed[..., None])
    cv2.imwrite(str(out / "dib_comic.jpg"), _comp(comic, a, bg), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 2) póster a dos tintas (negro, gris, dorado, crema) sin líneas
    pos = _bands(im, [0.28, 0.5, 0.74], ["#0A0A0A", "#3A3A38", "#F4C542", "#F5F5F2"], 11)
    cv2.imwrite(str(out / "dib_poster.jpg"), _comp(pos, a, bg * 0.6, 1.0), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 3) lápiz sobre papel claro (slide de contraste #E7E7E3)
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    sk = cv2.divide(g, 255 - cv2.GaussianBlur(255 - g, (0, 0), 8), scale=256).astype(np.float32) / 255
    sk = np.clip(sk, 0, 1) ** 2.2 * np.clip(_xdog(im, 0.8, eps=0.02) + 0.35, 0, 1)
    rng = np.random.default_rng(3); paper = _hex("#E7E7E3") - rng.normal(0, 4, im.shape[:2])[..., None]
    pen = paper * sk[..., None] + _hex("#1A1A18") * (1 - sk[..., None])
    a3 = a[..., None]; card = paper * (1 - a3) + pen * a3
    cv2.imwrite(str(out / "dib_lapiz.jpg"), np.clip(card, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 4) tinta con trama de puntos dorada
    gg = cv2.cvtColor(cv2.bilateralFilter(im, 9, 50, 9), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W]; cell = 9
    cxp = (xx % cell) - cell / 2; cyp = (yy % cell) - cell / 2
    r = np.sqrt(cxp ** 2 + cyp ** 2) / (cell / 2)
    dots = (r < np.clip(gg * 1.25, 0, 1.1)).astype(np.float32)
    ink2 = _xdog(im, 1.0, eps=0.01)
    ht = (_hex("#0A0A0A") * (1 - dots[..., None]) + _hex("#F4C542") * dots[..., None]) * ink2[..., None]
    ht = np.where((gg > 0.82)[..., None], _hex("#F5F5F2"), ht) * ink2[..., None]
    cv2.imwrite(str(out / "dib_trama.jpg"), _comp(ht, a, bg, 0.6), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 5) solo línea: contornos crema y sombras en dorado oscuro sobre negro
    sm5 = cv2.bilateralFilter(cv2.bilateralFilter(im, 9, 60, 9), 9, 60, 9)
    e5 = cv2.Canny(cv2.GaussianBlur(sm5, (0, 0), 1.3), 30, 90)
    e5 = cv2.GaussianBlur(cv2.dilate(e5, np.ones((2, 2), np.uint8)).astype(np.float32) / 255, (0, 0), 0.7)
    shade = _bands(im, [0.35, 0.7], ["#0A0A0A", "#1E1A0C", "#3A3014"], 15)
    line = shade * (1 - e5[..., None]) + _hex("#F5F5F2") * e5[..., None]
    cv2.imwrite(str(out / "dib_linea.jpg"), _comp(line, a, bg, 1.0), [cv2.IMWRITE_JPEG_QUALITY, 92])
    # 6) acuarela: manchas suaves, poca saturación, bordes que se funden, línea fina
    wc = cv2.stylization(cv2.pyrMeanShiftFiltering(im, 10, 28), sigma_s=60, sigma_r=0.45).astype(np.float32)
    wc = _grade(wc.astype(np.uint8), warm=0.16, contrast=0.95, sat=0.7)
    wc = wc * (0.75 + 0.25 * _xdog(im, 0.8, eps=0.02))[..., None]
    noise = cv2.GaussianBlur(np.random.default_rng(7).normal(0, 1, im.shape[:2]).astype(np.float32), (0, 0), 3)
    wc = wc * (1 + 0.04 * noise[..., None])
    cv2.imwrite(str(out / "dib_acuarela.jpg"), _comp(wc, a, bg, 0.7), [cv2.IMWRITE_JPEG_QUALITY, 92])

def dibujos(foto, out):
    import cv2
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(foto)); a = _cutout(img); im, a = _frame(img, a)
    estilos_dibujo(im, a, out)
    print(f"OK {out}/dib_comic, dib_poster, dib_lapiz, dib_trama, dib_linea, dib_acuarela (.jpg)")

# ---------- solo quitar el fondo y llevar la foto a la paleta del perfil ----------
def _gradient_map(gray, stops):
    """gray 0..1 -> color por tramos: stops = [(pos, "#hex"), ...]"""
    pos = np.array([p for p, _ in stops], np.float32); cols = np.stack([_hex(c) for _, c in stops])
    out = np.zeros(gray.shape + (3,), np.float32)
    for ch in range(3): out[..., ch] = np.interp(gray, pos, cols[:, ch])
    return out

def recortes(foto, out):
    import cv2
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    img = cv2.imread(str(foto)); a = _cutout(img); im, a = _frame(img, a)
    bg = _background()
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    lo, hi = np.percentile(g[a > 0.5], 1), np.percentile(g[a > 0.5], 99.5)
    g = np.clip((g - lo) / (hi - lo + 1e-6), 0, 1)
    # 1) paleta del perfil: negro -> gris cálido -> dorado -> crema (la foto, en los colores de la marca)
    pal = _gradient_map(g, [(0, "#0A0A0A"), (0.38, "#3A3428"), (0.66, "#F4C542"), (1, "#F5F5F2")])
    cv2.imwrite(str(out / "rec_paleta.jpg"), _comp(pal, a, bg, 0.7), [cv2.IMWRITE_JPEG_QUALITY, 93])
    # 2) blanco y negro con contraste y luces cálidas (más sobrio)
    bn = _gradient_map(g ** 1.1, [(0, "#0A0A0A"), (0.55, "#7A7670"), (0.85, "#E7E1CF"), (1, "#F5F5F2")])
    cv2.imwrite(str(out / "rec_bn.jpg"), _comp(bn, a, bg, 0.7), [cv2.IMWRITE_JPEG_QUALITY, 93])
    # 3) color natural apagado con tinte dorado (se reconoce la foto, pero ya "es" del perfil)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= 0.45
    col = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    col = col * 0.72 + pal * 0.28
    col = np.clip((col - 128) * 1.08 + 128, 0, 255)
    cv2.imwrite(str(out / "rec_calido.jpg"), _comp(col, a, bg, 0.7), [cv2.IMWRITE_JPEG_QUALITY, 93])
    # 4) la foto original solo sin fondo (referencia)
    cv2.imwrite(str(out / "rec_original.jpg"), _comp(im.astype(np.float32), a, bg, 0.7), [cv2.IMWRITE_JPEG_QUALITY, 93])
    print(f"OK {out}/rec_paleta, rec_bn, rec_calido, rec_original (.jpg)")

def main():
    a = sys.argv[1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if not a: sys.exit(__doc__)
    if a[0] == "candidatos": candidatos(a[1], a[2], int(opt("--n", 15)), opt("--fuentes") and opt("--fuentes").split(","))
    elif a[0] == "hacer": hacer(a[1], a[2], opt("--credito"))
    elif a[0] == "dibujo": dibujos(a[1], a[2])
    elif a[0] == "recorte": recortes(a[1], a[2])
    else: sys.exit(__doc__)

if __name__ == "__main__":
    main()
