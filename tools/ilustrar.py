#!/usr/bin/env python3
"""Ilustraciones realistas a partir de fotos con licencia libre (para cuando una foto no queda bien en un Reel).

La ilustración se hace SOBRE la foto real (no se inventa la cara): recorta a la persona, la pinta con un acabado de
ilustración y la coloca sobre el fondo de la marca. Así la cara es la de la foto, pero con estética propia.

Uso:
  python3 tools/ilustrar.py candidatos "<persona>" <carpeta> [--n 10]
      -> descarga las N mejores fotos de Wikimedia Commons (licencia libre) a <carpeta>/cand_NN.jpg,
         hoja de contacto <carpeta>/candidatos.jpg y lista con autor/licencia/tamaño en <carpeta>/candidatos.json
  python3 tools/ilustrar.py hacer <foto.jpg> <carpeta> [--credito "Foto: X / Wikimedia Commons, CC BY-SA 2.0"]
      -> <carpeta>/ilus_pintura.jpg, ilus_editorial.jpg, ilus_duotono.jpg (1080x1350) + recorte transparente .png
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
GOLD = np.array([66, 197, 244], np.float32)   # BGR de #F4C542
BG = np.array([10, 10, 10], np.float32)

def candidatos(persona, out, n=10):
    import assets, cv2
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    cs = assets.search_commons(persona, n * 2)
    cs = sorted(cs, key=lambda c: -(c["w"] or 0) * (c["h"] or 0))[:n]
    lst = []
    for i, c in enumerate(cs, 1):
        f = out / f"cand_{i:02d}.jpg"; f.write_bytes(assets.get(c["url"]))
        lst.append({"n": i, "archivo": f.name, **{k: c[k] for k in ("id", "autor", "licencia", "w", "h", "pagina", "desc", "credito")}})
        print(f"{i}. {c['licencia']} · {c['w']}x{c['h']} · {c['autor'][:40]} · {c['id']}")
    (out / "candidatos.json").write_text(json.dumps(lst, ensure_ascii=False, indent=1), encoding="utf-8")
    th = []
    for c in lst:
        im = cv2.imread(str(out / c["archivo"]))
        if im is None: continue
        s = 320 / max(im.shape[:2]); im = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        cell = np.full((360, 320, 3), 10, np.uint8); y = (320 - im.shape[0]) // 2; x = (320 - im.shape[1]) // 2
        cell[y:y + im.shape[0], x:x + im.shape[1]] = im
        cv2.putText(cell, f"{c['n']}  {c['w']}x{c['h']}", (8, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (66, 197, 244), 2)
        th.append(cell)
    cols = 5; rows = (len(th) + cols - 1) // cols
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

def main():
    a = sys.argv[1:]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if not a: sys.exit(__doc__)
    if a[0] == "candidatos": candidatos(a[1], a[2], int(opt("--n", 10)))
    elif a[0] == "hacer": hacer(a[1], a[2], opt("--credito"))
    else: sys.exit(__doc__)

if __name__ == "__main__":
    main()
