#!/usr/bin/env python3
"""Lee las estadísticas de los Reels de @capital.sin.filtros (API oficial de Instagram) y las guarda en stats/.

Uso (lo ejecuta el workflow .github/workflows/stats-reels.yml cada día; también a mano):
  IG_TOKEN=... [IG_USER_ID=...] python3 tools/ig_stats.py [--dias 60]

- IG_TOKEN: token de acceso de larga duración de la cuenta (secreto de GitHub, NUNCA en el repo).
  · Token de "Instagram API con inicio de sesión de Instagram" (empieza por "IG..."): usa graph.instagram.com/me.
  · Token de "inicio de sesión de Facebook" (empieza por "EAA..."): usa graph.facebook.com/<IG_USER_ID>.
- Escribe stats/reels.json (todas las métricas, por Reel) y stats/resum.md (tabla para leer rápido).
  Solo métricas agregadas de los vídeos: ni tokens ni datos de personas.
- Cruza cada vídeo con su slug comparando el caption con posts/<slug>/post.json, y calcula el % visto de media
  (tiempo medio de visualización ÷ duración del mp4).

Métricas (las que la API dé para cada Reel): views (reproducciones), reach (cuentas alcanzadas), ig_reels_avg_watch_time
(tiempo medio, ms), ig_reels_video_view_total_time (ms), likes, comments, shares (envíos), saved (guardados),
total_interactions, follows (seguidores ganados, si está disponible).
"""
import json, os, re, sys, pathlib, subprocess, datetime, urllib.request, urllib.parse, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "stats"
VER = "v22.0"
METRICS = ["views", "reach", "ig_reels_avg_watch_time", "ig_reels_video_view_total_time", "likes", "comments",
           "shares", "saved", "total_interactions", "follows"]

def get(url, params):
    q = urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(f"{url}?{q}", timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(body).get("error", {})
        except Exception:
            err = {"message": body[:300]}
        raise RuntimeError(f"HTTP {e.code}: {err.get('message')} (code {err.get('code')})")

def norm(s):
    s = re.sub(r"[^\w]+", " ", (s or "").lower()).strip()
    return s[:80]

def slugs_by_caption():
    m = {}
    for pj in ROOT.glob("posts/*/post.json"):
        try:
            d = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("caption"):
            m[norm(d["caption"])] = pj.parent.name
    return m

def duration(slug):
    f = ROOT / "posts" / slug / "reel.mp4"
    if not slug or not f.exists():
        return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return float(out)
    except Exception:
        return None

def insights(base, mid, tok):
    got = {}
    try:
        d = get(f"{base}/{mid}/insights", {"metric": ",".join(METRICS), "access_token": tok})
        for it in d.get("data", []):
            v = it.get("values", [{}])[0].get("value") if it.get("values") else it.get("total_value", {}).get("value")
            got[it["name"]] = v
        return got
    except RuntimeError:
        pass
    for m in METRICS:  # alguna métrica no está disponible: se piden de una en una
        try:
            d = get(f"{base}/{mid}/insights", {"metric": m, "access_token": tok})
            for it in d.get("data", []):
                got[it["name"]] = it.get("values", [{}])[0].get("value") if it.get("values") else it.get("total_value", {}).get("value")
        except RuntimeError:
            continue
    return got

def main():
    tok = os.environ.get("IG_TOKEN", "").strip()
    if not tok:
        sys.exit("Falta IG_TOKEN (secreto de GitHub). Ver docs/estadisticas.md.")
    dias = int(sys.argv[sys.argv.index("--dias") + 1]) if "--dias" in sys.argv else 60
    if tok.startswith("IG"):
        base, me = f"https://graph.instagram.com/{VER}", "me"
    else:
        uid = os.environ.get("IG_USER_ID", "").strip()
        if not uid:
            sys.exit("Con un token de Facebook (EAA...) hace falta IG_USER_ID.")
        base, me = f"https://graph.facebook.com/{VER}", uid
    desde = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=dias)
    caps = slugs_by_caption()
    rows, url, params = [], f"{base}/{me}/media", {
        "fields": "id,caption,media_type,media_product_type,permalink,timestamp", "limit": 50, "access_token": tok}
    while url:
        d = get(url, params) if params else json.load(urllib.request.urlopen(url, timeout=60))
        params = None
        stop = False
        for m in d.get("data", []):
            ts = datetime.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            if ts < desde:
                stop = True; break
            if m.get("media_product_type") != "REELS" and m.get("media_type") != "VIDEO":
                continue
            slug = caps.get(norm(m.get("caption")))
            ins = insights(base, m["id"], tok)
            dur = duration(slug)
            avg = (ins.get("ig_reels_avg_watch_time") or 0) / 1000
            reach = ins.get("reach") or 0
            rows.append({"slug": slug, "fecha": m["timestamp"], "permalink": m.get("permalink"),
                         "primera_linea": (m.get("caption") or "").split("\n")[0][:120],
                         "duracion_s": round(dur, 1) if dur else None, "media_vista_s": round(avg, 1),
                         "pct_visto": round(100 * avg / dur) if dur and avg else None,
                         "envios_por_1000_alcance": round(1000 * (ins.get("shares") or 0) / reach, 1) if reach else None,
                         **ins})
        url = None if stop else d.get("paging", {}).get("next")
    OUT.mkdir(exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    (OUT / "reels.json").write_text(json.dumps({"actualizado": now, "reels": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"# Estadísticas de los Reels (actualizado {now})", "",
             "| Fecha | Reel | Dura | Vista media | % visto | Reprod. | Alcance | Envíos | Guard. | Likes | Coment. | Seguid. |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        name = r["slug"] or r["primera_linea"][:40]
        lines.append(f"| {r['fecha'][:10]} | {name} | {r['duracion_s'] or '–'} s | {r['media_vista_s']} s | "
                     f"{str(r['pct_visto']) + ' %' if r['pct_visto'] is not None else '–'} | {r.get('views', '–')} | "
                     f"{r.get('reach', '–')} | {r.get('shares', '–')} | {r.get('saved', '–')} | {r.get('likes', '–')} | "
                     f"{r.get('comments', '–')} | {r.get('follows', '–')} |")
    if rows:
        best = max(rows, key=lambda r: (r["pct_visto"] or 0))
        lines += ["", f"Más visto en proporción: **{best['slug'] or best['primera_linea'][:40]}** ({best['pct_visto']} % de media)."]
    (OUT / "resum.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: {len(rows)} Reels -> stats/reels.json y stats/resum.md")

if __name__ == "__main__":
    main()
