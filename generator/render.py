#!/usr/bin/env python3
"""Renderiza un carrusel de Capital Sin Filtros a partir de un spec JSON.

Uso:
  python3 generator/render.py generator/specs/<slug>.json
Salida:
  posts/<slug>/01.jpg ... (1080x1350, JPG) y posts/<slug>/preview.png (mosaico para revisar)

Tipos de slide (campo "type"):
  hook     -> title, subtitle_html?, svg?
  content  -> kicker?, title_html, body_html?, svg?, source?, theme ("dark"|"light")
  stat     -> kicker?, label_top?, big, label_bottom?, svg?, source?
  rows     -> kicker?, rows [[izq, der], ...], body_html?, icons? (lista de svg 64x64 por fila)
  cta      -> kicker?, title_html, body_html?, svg?
Campos comunes opcionales: theme, title_size (px), svg_bottom (px, por defecto 170), style (CSS extra para la slide).
"svg": SVG en línea de hasta 888 px de ancho y ~460 px de alto; se coloca en la parte inferior.
Usa SOLO la paleta de marca: #0A0A0A #F4C542 #F5F5F2 #6F6F6F #E7E7E3 (+ #CFCFCA, #2a2a2a para matices).
"""
import json, sys, pathlib, html as H

ROOT = pathlib.Path(__file__).resolve().parent.parent

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#333;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;background:#0A0A0A;color:#F5F5F2;padding:190px 96px 170px;display:flex;flex-direction:column;justify-content:flex-start}
.s.light{background:#E7E7E3;color:#0A0A0A}
.s.center{justify-content:center;padding-top:150px}
.n{position:absolute;top:64px;left:96px;font-size:26px;font-weight:600;color:#6F6F6F;letter-spacing:.04em}
.logo{position:absolute;bottom:64px;left:50%;transform:translateX(-50%);font-weight:800;font-size:34px;color:#F4C542;letter-spacing:.02em}
.light .logo{color:#0A0A0A}
.swipe{position:absolute;bottom:68px;right:96px;font-size:26px;font-weight:600;color:#6F6F6F}
.k{font-size:30px;font-weight:600;color:#F4C542;letter-spacing:.12em;text-transform:uppercase;margin-bottom:40px}
.light .k{color:#8A6A00}
h1{font-size:92px;line-height:1.03;font-weight:800;letter-spacing:-.035em}
h2{font-size:76px;line-height:1.07;font-weight:800;letter-spacing:-.03em}
p{font-size:40px;line-height:1.38;font-weight:400;margin-top:40px;color:#CFCFCA}
.light p{color:#3a3a3a}
.g{color:#F4C542}.light .g{color:#8A6A00}
b{color:#F5F5F2}.light b{color:#0A0A0A}
.big{white-space:nowrap;font-size:172px;font-weight:800;letter-spacing:-.05em;line-height:1;color:#F4C542;margin:24px 0 8px}
.light .big{color:#0A0A0A}
.lab{font-size:38px;font-weight:500;color:#CFCFCA}.light .lab{color:#3a3a3a}
.src{position:absolute;bottom:120px;left:96px;right:96px;font-size:24px;color:#6F6F6F;line-height:1.4}
.row{display:flex;justify-content:space-between;align-items:center;border-top:2px solid #2a2a2a;padding:34px 0;gap:24px}
.row:last-of-type{border-bottom:2px solid #2a2a2a}
.light .row{border-color:#c9c9c4}
.row .a{font-size:40px;color:#CFCFCA;display:flex;align-items:center}.light .row .a{color:#3a3a3a}
.row .b{font-size:50px;font-weight:800;text-align:right}
.ill{position:absolute;left:96px}
"""

def esc(t): return H.escape(t or "")

def slide_html(i, n, s):
    t = s.get("type", "content")
    theme = s.get("theme", "dark")
    classes = ["s"] + (["light"] if theme == "light" else [])
    if t == "rows" or s.get("center"):
        classes.append("center")
    parts = [f'<div class="n">{i:02d}/{n:02d}</div>']
    if s.get("kicker"):
        parts.append(f'<div class="k">{esc(s["kicker"])}</div>')
    ts = f' style="font-size:{s["title_size"]}px"' if s.get("title_size") else ""
    if t == "hook":
        parts.append(f'<h1{ts}>{s["title"]}</h1>')
        if s.get("subtitle_html"):
            parts.append(f'<p style="max-width:{s.get("subtitle_width", 860)}px">{s["subtitle_html"]}</p>')
    elif t == "stat":
        if s.get("label_top"): parts.append(f'<div class="lab">{s["label_top"]}</div>')
        bs = f' style="font-size:{s["big_size"]}px"' if s.get("big_size") else ""
        parts.append(f'<div class="big"{bs}>{s["big"]}</div>')
        if s.get("label_bottom"): parts.append(f'<div class="lab">{s["label_bottom"]}</div>')
    elif t == "rows":
        icons = s.get("icons") or []
        for j, (a, b) in enumerate(s["rows"]):
            ic = f'<svg viewBox="0 0 64 64" width="64" height="64" style="margin-right:28px;flex:none">{icons[j]}</svg>' if j < len(icons) and icons[j] else ""
            parts.append(f'<div class="row"><span class="a">{ic}{a}</span><span class="b">{b}</span></div>')
        if s.get("body_html"): parts.append(f'<p>{s["body_html"]}</p>')
    else:  # content / cta
        parts.append(f'<h2{ts}>{s["title_html"]}</h2>')
        if s.get("body_html"): parts.append(f'<p>{s["body_html"]}</p>')
    if s.get("svg"):
        parts.append(f'<div class="ill" style="bottom:{s.get("svg_bottom", 170)}px">{s["svg"]}</div>')
    if s.get("source"):
        parts.append(f'<div class="src">{esc(s["source"])}</div>')
    parts.append('<div class="logo">CSF</div>')
    if i == 1:
        parts.append('<div class="swipe">Desliza →</div>')
    st = f' style="{s["style"]}"' if s.get("style") else ""
    return f'<div class="{" ".join(classes)}" id="s{i}"{st}>' + "".join(parts) + "</div>"

def main():
    spec_path = pathlib.Path(sys.argv[1])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slug, slides = spec["slug"], spec["slides"]
    if not 2 <= len(slides) <= 10:
        sys.exit("Un carrusel necesita entre 2 y 10 slides.")
    n = len(slides)
    doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>' + \
          "".join(slide_html(i + 1, n, s) for i, s in enumerate(slides)) + "</body></html>"
    out = ROOT / "posts" / slug
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    html_path = out.parent.parent / "generator" / ".last_render.html"
    html_path.write_text(doc, encoding="utf-8")
    from playwright.sync_api import sync_playwright
    from PIL import Image
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg.goto(html_path.as_uri())
        pg.evaluate("document.fonts.ready")
        for i in range(1, n + 1):
            png = out / f"_{i:02d}.png"
            pg.locator(f"#s{i}").screenshot(path=str(png))
            Image.open(png).convert("RGB").save(out / f"{i:02d}.jpg", quality=92)
            png.unlink()
        b.close()
    ims = [Image.open(out / f"{i:02d}.jpg").resize((360, 450)) for i in range(1, n + 1)]
    cols = 5
    rows = (n + cols - 1) // cols
    grid = Image.new("RGB", (cols * 368, rows * 458), "#888")
    for k, im in enumerate(ims):
        grid.paste(im, ((k % cols) * 368, (k // cols) * 458))
    prev = ROOT / "generator" / ".preview.png"
    grid.save(prev)
    print(f"OK {n} slides -> posts/{slug}/  | revisar: {prev}")

if __name__ == "__main__":
    main()
