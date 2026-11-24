#!/usr/bin/env python3
"""Busca y descarga imágenes y sonidos con licencia libre para un Reel, y guarda el crédito de cada uno.

Uso:
  python3 tools/assets.py buscar unsplash|commons|openverse|openverse-audio "<consulta>" [--n 6]
      -> lista candidatos (id, autor, licencia, tamaño, url) para elegir.
  python3 tools/assets.py bajar <slug> <id_local> unsplash|commons|openverse|openverse-audio "<consulta o id>" [--elige 1] [--orient portrait]
      -> descarga el candidato N (1 = el primero) a posts/<slug>/assets/<id_local>.jpg (.wav para audio)
  python3 tools/assets.py resolver generator/specs/<slug>.json
      -> descarga lo que falte de la lista "assets" del spec:
         "assets": [{"id": "jensen", "de": "commons", "q": "Jensen Huang", "elige": 1},
                    {"id": "bolsa", "de": "unsplash", "q": "stock market screen", "orient": "portrait"},
                    {"id": "campana", "de": "openverse-audio", "q": "bell ring"}]
         "alt": consulta de reserva si "q" (p. ej. un "File:..." exacto de Commons) no da resultado.
         "recorte": "real" | "bn" (personas): quita el fondo y deja la foto sobre el fondo de la marca, en color natural
                    o en blanco y negro cálido (estilos elegidos por Pol). "cerca": false para plano más abierto.
  python3 tools/assets.py hoja <slug>     -> posts/<slug>/assets/hoja.jpg (miniaturas para revisar)

Créditos en posts/<slug>/assets/creditos.json: {"jensen": {"credito": "Foto: ... / Wikimedia Commons, CC BY 3.0", ...}}.
Pon ese texto en el "credito" del componente data-photo (o en un .src). Solo se aceptan licencias que permiten uso
comercial y modificación: CC0, dominio público, CC BY, CC BY-SA (Unsplash: licencia Unsplash, crédito "Foto: X / Unsplash").
Unsplash necesita la variable UNSPLASH_ACCESS_KEY (secreto del repo en GitHub Actions). Commons, nada. Openverse, desde
GitHub, OPENVERSE_CLIENT_ID y OPENVERSE_CLIENT_SECRET (registro gratuito, ver docs/reels.md).
Imágenes de personas: solo figuras públicas y fotos con licencia libre (normalmente Commons); nunca retocadas.
"""
import json, os, sys, pathlib, subprocess, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "csf-media-assets/1.0 (+https://github.com/dineroaldescubierto15-blip/csf-media)"}
OK_LIC = ("cc0", "pdm", "by", "by-sa", "public domain", "cc-by", "cc by", "cc-by-sa", "cc by-sa", "pd", "cc zero", "unsplash")

def get(url, headers=None, tries=5):
    import time, urllib.error
    for k in range(tries):
        req = urllib.request.Request(url, headers={**UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and k < tries - 1:
                time.sleep(int(e.headers.get("Retry-After") or 0) or 5 * (k + 1)); continue
            raise

def getj(url, headers=None):
    return json.loads(get(url, headers))

def lic_ok(lic):
    l = (lic or "").lower().strip()
    return bool(l) and not any(x in l for x in ("nc", "nd", "fair use", "non-free")) and any(l.startswith(x) or x in l for x in OK_LIC)

def search_unsplash(q, n=6, orient=None):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        sys.exit("Falta UNSPLASH_ACCESS_KEY (en GitHub Actions es un secreto del repositorio).")
    url = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(
        {"query": q, "per_page": n, "content_filter": "high", **({"orientation": orient} if orient else {})})
    res = getj(url, {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"})["results"]
    return [{"id": r["id"], "autor": r["user"]["name"], "licencia": "Unsplash", "w": r["width"], "h": r["height"],
             "url": r["urls"]["raw"] + "&w=1600&fm=jpg&q=85", "pagina": r["links"]["html"],
             "download_location": r["links"]["download_location"], "desc": r.get("alt_description") or "",
             "credito": f"Foto: {r['user']['name']} / Unsplash", "fuente": "unsplash"} for r in res]

def search_commons(q, n=6, orient=None):
    if q.startswith("File:"):
        titles = [q]
    else:
        s = getj("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "query", "list": "search", "srsearch": q, "srnamespace": 6, "srlimit": min(50, n * 3), "format": "json"}))
        if "query" not in s:
            sys.exit(f"Commons no ha devuelto resultados: {json.dumps(s)[:300]}")
        titles = [x["title"] for x in s["query"]["search"] if x["title"].lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"))]
    out = []
    for i in range(0, len(titles), 20):
        info = getj("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "query", "titles": "|".join(titles[i:i + 20]), "prop": "imageinfo", "iiprop": "url|size|extmetadata",
             "iiurlwidth": 1600, "format": "json"}))
        for pg in info["query"]["pages"].values():
            ii = (pg.get("imageinfo") or [None])[0]
            if not ii: continue
            md = ii.get("extmetadata", {})
            lic = md.get("LicenseShortName", {}).get("value", "")
            if not lic_ok(lic): continue
            import re
            autor = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip() or "autor desconocido"
            out.append({"id": pg["title"], "autor": autor[:80], "licencia": lic, "w": ii["width"], "h": ii["height"],
                        "url": ii.get("thumburl") or ii["url"], "pagina": ii["descriptionurl"],
                        "desc": re.sub("<[^>]+>", "", md.get("ImageDescription", {}).get("value", ""))[:120],
                        "credito": f"Foto: {autor[:60]} / Wikimedia Commons, {lic}", "fuente": "commons"})
    return out[:n]

_ov_tok = None
def openverse_token():
    """Token de Openverse a partir de OPENVERSE_CLIENT_ID y OPENVERSE_CLIENT_SECRET (registro gratuito; caduca a las 12 h)."""
    global _ov_tok
    if _ov_tok is None:
        cid, sec = os.environ.get("OPENVERSE_CLIENT_ID"), os.environ.get("OPENVERSE_CLIENT_SECRET")
        _ov_tok = ""
        if cid and sec:
            body = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": sec}).encode()
            req = urllib.request.Request("https://api.openverse.org/v1/auth_tokens/token/", data=body,
                                         headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
            import urllib.error
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    _ov_tok = json.loads(r.read())["access_token"]
            except urllib.error.HTTPError as e:
                det = e.read().decode("utf-8", "replace")[:300]
                raise SystemExit(f"Openverse no da token (HTTP {e.code}): {det}. ¿Está verificado el correo del registro?")
    return _ov_tok

def search_openverse(q, n=6, orient=None, audio=False):
    kind = "audio" if audio else "images"
    p = {"q": q, "page_size": n * 2, "license": "cc0,pdm,by,by-sa", "mature": "false"}
    if audio: p["extension"] = "wav,mp3,ogg,flac"
    if orient and not audio: p["aspect_ratio"] = {"portrait": "tall", "landscape": "wide", "squarish": "square"}.get(orient, orient)
    tok = openverse_token()   # desde algunas IPs (p. ej. GitHub) Openverse pide registrarse (gratis)
    res = getj(f"https://api.openverse.org/v1/{kind}/?" + urllib.parse.urlencode(p), {"Authorization": f"Bearer {tok}"} if tok else None)["results"]
    out = []
    for r in res:
        lic = f"CC {r['license'].upper()} {r.get('license_version') or ''}".strip().replace("CC CC0", "CC0").replace("CC PDM", "Dominio público")
        out.append({"id": r["id"], "autor": (r.get("creator") or "autor desconocido")[:80], "licencia": lic,
                    "w": r.get("width"), "h": r.get("height"), "dur": (r.get("duration") or 0) / 1000 if audio else None,
                    "url": r["url"], "pagina": r.get("foreign_landing_url"), "desc": r.get("title", "")[:120],
                    "credito": f"{'Sonido' if audio else 'Foto'}: {(r.get('creator') or 'autor desconocido')[:60]} / {r.get('source','Openverse')}, {lic}",
                    "fuente": f"openverse:{r.get('source')}"})
    if audio:
        out = [x for x in out if not x["dur"] or x["dur"] <= 12]
    return out[:n]

def search(src, q, n=6, orient=None):
    if src == "unsplash": return search_unsplash(q, n, orient)
    if src == "commons": return search_commons(q, n, orient)
    if src == "openverse": return search_openverse(q, n, orient)
    if src == "openverse-audio": return search_openverse(q, n, audio=True)
    sys.exit(f"Fuente desconocida: {src}")

def download(slug, lid, src, q, pick=1, orient=None):
    cands = search(src, q, max(pick, 6), orient)
    if len(cands) < pick:
        sys.exit(f"Sin resultados con licencia válida para «{q}» en {src}")
    c = cands[pick - 1]
    d = ROOT / "posts" / slug / "assets"; d.mkdir(parents=True, exist_ok=True)
    raw = get(c["url"])
    if src == "openverse-audio":
        tmp = d / f".{lid}.src"; tmp.write_bytes(raw); dest = d / f"{lid}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-ac", "1", "-ar", "48000", "-t", "12", str(dest)], check=True)
        tmp.unlink()
    else:
        tmp = d / f".{lid}.src"; tmp.write_bytes(raw); dest = d / f"{lid}.jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-vf", "scale='min(1600,iw)':-2", "-q:v", "3", str(dest)], check=True)
        tmp.unlink()
    if src == "unsplash":   # requisito de la API de Unsplash: notificar la descarga
        try: get(c["download_location"], {"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"})
        except Exception: pass
    cf = d / "creditos.json"; cr = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {}
    cr[lid] = {k: c.get(k) for k in ("credito", "autor", "licencia", "fuente", "pagina", "desc")} | {"consulta": q, "archivo": dest.name}
    cf.write_text(json.dumps(cr, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK {dest.relative_to(ROOT)}  ·  {c['credito']}")
    return dest

def resolve(spec_path):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8")); slug = spec["slug"]
    for a in spec.get("assets", []):
        ext = "wav" if a["de"] == "openverse-audio" else "jpg"
        dest = ROOT / "posts" / slug / "assets" / f"{a['id']}.{ext}"
        if dest.exists():
            print(f"ya está: {a['id']}"); continue
        try:
            download(slug, a["id"], a["de"], a["q"], int(a.get("elige", 1)), a.get("orient"))
        except BaseException as e:
            if isinstance(e, KeyboardInterrupt): raise
            alt = a.get("alt")
            if a["de"] == "openverse" and not alt:      # Openverse sin registro falla desde GitHub: prueba Commons
                print(f"  Openverse no disponible ({e}); pruebo Wikimedia Commons")
                download(slug, a["id"], "commons", a["q"], 1, a.get("orient")); alt = None
            elif not alt:
                raise
            else:
                print(f"  sin resultado para «{a['q']}», pruebo «{alt}»")
                download(slug, a["id"], a["de"], alt, 1, a.get("orient"))
        if a.get("recorte"):   # persona: quitar el fondo ("real" = color natural, "bn" = blanco y negro cálido)
            recortar(dest, a["recorte"], a.get("cerca", True))

def recortar(dest, estilo="real", cerca=True):
    """Sustituye la foto por la persona sin fondo sobre el fondo de la marca (guarda la original como <id>_orig.jpg)."""
    import shutil, tempfile
    orig = dest.with_name(dest.stem + "_orig.jpg"); shutil.copy(dest, orig)
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [sys.executable, str(ROOT / "tools" / "ilustrar.py"), "recorte", str(orig), tmp] + (["--cerca"] if cerca else [])
        subprocess.run(cmd, check=True)
        shutil.copy(pathlib.Path(tmp) / {"real": "rec_original.jpg", "bn": "rec_bn.jpg", "paleta": "rec_paleta.jpg",
                                          "calido": "rec_calido.jpg"}[estilo], dest)
    print(f"  recorte «{estilo}»: {dest.name} (original en {orig.name})")

def sheet(slug):
    d = ROOT / "posts" / slug / "assets"; imgs = sorted(d.glob("*.jpg"))
    imgs = [i for i in imgs if i.name != "hoja.jpg"]
    if not imgs: sys.exit("No hay imágenes")
    from PIL import Image, ImageDraw
    th = []
    for f in imgs:
        im = Image.open(f).convert("RGB"); im.thumbnail((360, 360)); c = Image.new("RGB", (360, 400), "#0A0A0A")
        c.paste(im, ((360 - im.width) // 2, (360 - im.height) // 2)); ImageDraw.Draw(c).text((8, 372), f.stem, fill="#F4C542"); th.append(c)
    cols = min(4, len(th)); rows = (len(th) + cols - 1) // cols
    out = Image.new("RGB", (cols * 360, rows * 400), "#0A0A0A")
    for i, t in enumerate(th): out.paste(t, ((i % cols) * 360, (i // cols) * 400))
    out.save(d / "hoja.jpg", quality=85); print(f"OK {(d / 'hoja.jpg').relative_to(ROOT)}")

def main():
    a = sys.argv[1:]
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    if not a: sys.exit(__doc__)
    if a[0] == "buscar":
        for i, c in enumerate(search(a[1], a[2], int(opt("--n", 6)), opt("--orient")), 1):
            extra = f"{c['dur']:.1f}s" if c.get("dur") else f"{c.get('w')}x{c.get('h')}"
            print(f"{i}. {c['licencia']} · {c['autor']} · {extra} · {c['desc'][:70]}\n   {c['pagina']}")
    elif a[0] == "bajar":
        download(a[1], a[2], a[3], a[4], int(opt("--elige", 1)), opt("--orient"))
    elif a[0] == "resolver":
        resolve(a[1])
    elif a[0] == "hoja":
        sheet(a[1])
    else:
        sys.exit(__doc__)

if __name__ == "__main__":
    main()
