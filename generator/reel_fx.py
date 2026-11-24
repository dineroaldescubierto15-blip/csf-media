"""Extras visuales y de sonido para generator/reel.py (no toca la voz).

Lo usa reel.py para:
  - head(spec, slug, subs): <base>, GSAP y CSS/JS extra (animaciones, transiciones, fondo, subtítulos).
  - expand(html): componentes de alto nivel -> HTML (iconos, gráficos, titulares, fotos).
  - cues(spec, starts) y sfx_track(cues, total): efectos de sonido sincronizados con lo que aparece.
  - subs_timing(...): subtítulos palabra a palabra sincronizados con la voz.

Componentes (dentro del "html" de una escena):
  <i data-icon="lucide:trending-up" data-size="140" class="g" data-in="0.3" data-a="pop" data-sfx="pop"></i>
      lucide:<nombre> (1.500 iconos de línea, ISC) | si:<marca> (Simple Icons, CC0: si:bitcoin, si:ethereum, si:nvidia...).
      Color: clase .g (dorado), .w (blanco), .m (gris) o style="color:...".
  <div data-chart='{"type":"line","data":[...],"labels":["ene","jun","nov"],"unit":" $","in":0.3,"d":1.6,
                    "mark":-1,"sfx":"riser"}'></div>     -> gráfico SVG con datos reales (line | bar).
      bar: "labels" una por barra; "colors" opcional; "mark": índice destacado en dorado.
  <div data-news='{"medio":"Expansión","fecha":"21/11/2026","titular":"El BCE **sube** los tipos","in":0.2}'></div>
      -> tarjeta de titular (texto citado, sin logos del medio). **palabra** = subrayado dorado animado.
  <div data-photo='{"src":"assets/jensen.jpg","credito":"auto","h":760,"in":0.1}'></div>
      -> foto con marco, zoom lento (Ken Burns) y crédito. Archivos en posts/<slug>/assets/ (tools/assets.py).
      "credito": "auto" toma el texto de posts/<slug>/assets/creditos.json (o escríbelo a mano).

Animaciones extra por atributo (además de up|fade|pop|grow|growy|draw|count de reel.py):
  data-a="slide" (desde la derecha) | "left" | "zoom" (de grande a normal) | "stamp" (golpe) | "blur" | "words"
  (palabra a palabra) | "type" (letra a letra) | "hl" (subrayado dorado que se dibuja) | "kb" (zoom lento toda la
  escena) | "float" (flota suave, continuo) | "shake" (sacudida corta) | "spin" (gira y aparece)
GSAP (timelines deterministas, mismo contrato que HyperFrames): dentro de la escena i,
  <script>const tl = TL(i); tl.from("#x", {y: 80, opacity: 0, duration: .5, ease: "back.out(2)"}, 0.3);</script>
  reel.py hace tl.seek(t) en cada fotograma. Plugins cargados: SplitText, TextPlugin, DrawSVGPlugin, MorphSVGPlugin,
  CustomEase. No uses timers, Date.now() ni Math.random() sin semilla.
Transición de salida por escena: "trans": "fade" (por defecto) | "slide" | "zoom" | "whip" | "cut".
Sonido: data-sfx="pop" en cualquier elemento con data-in (suena cuando aparece), o "sfx": [{"t": 1.2, "s": "impact", "v": 0.8}]
  en la escena. Por defecto suena un whoosh suave en cada cambio de escena ("sfx_transiciones": false lo quita).
  Biblioteca: generator/sfx/*.wav (ver generator/sfx/CREDITS.md). El pico del sonido cae en el instante indicado.
Spec global: "fondo": "grid" (por defecto) | "glow" | "none";  "subtitulos": true (palabra a palabra, abajo).
"""
import json, re, html as _html, pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
NM = ROOT / "node_modules"
SFX_DIR = ROOT / "generator" / "sfx"
SR = 48000

EXTRA_CSS = """
.w{color:#F5F5F2}.m{color:#8A8A85}
.icon{display:inline-flex;align-items:center;justify-content:center;line-height:0}
.icon svg{width:100%;height:100%}
.row{display:flex;align-items:center;gap:40px}
.col{display:flex;flex-direction:column;gap:24px}
.center{align-items:center;text-align:center}
.chip{display:inline-block;padding:14px 28px;border-radius:999px;background:#1C1C1A;border:2px solid #2E2E2B;font-size:36px;font-weight:600;color:#F5F5F2}
.chip.gold{background:#F4C542;color:#0A0A0A;border-color:#F4C542}
.card{background:#151514;border:2px solid #262624;border-radius:28px;padding:44px}
.news{background:#F5F5F2;color:#0A0A0A;border-radius:24px;padding:44px 48px 48px;box-shadow:0 30px 80px rgba(0,0,0,.55)}
.news .nm{display:flex;justify-content:space-between;align-items:center;font-size:30px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#0A0A0A;border-bottom:3px solid #0A0A0A;padding-bottom:18px;margin-bottom:28px}
.news .nm span{font-weight:500;color:#5A5A56;letter-spacing:0;text-transform:none}
.news .nt{font-size:62px;line-height:1.12;font-weight:800;letter-spacing:-.02em}
.news .nq{font-size:28px;color:#5A5A56;margin-top:24px}
.hl{background-image:linear-gradient(#F4C542,#F4C542);background-repeat:no-repeat;background-position:0 88%;background-size:0% 22%}
.news .hl{background-size:0% 30%}
.photo{position:relative;border-radius:28px;overflow:hidden;background:#151514}
.photo img{width:100%;height:100%;object-fit:cover;display:block;transform-origin:50% 40%}
.photo .cr{position:absolute;left:0;right:0;bottom:0;padding:60px 28px 18px;font-size:24px;color:#CFCFCA;background:linear-gradient(transparent,rgba(0,0,0,.75))}
.big2{font-size:132px;font-weight:800;letter-spacing:-.045em;line-height:1}
#bgfx{position:absolute;inset:-200px;pointer-events:none;opacity:.5}
#bgfx.grid{background-image:linear-gradient(rgba(245,245,242,.045) 2px,transparent 2px),linear-gradient(90deg,rgba(245,245,242,.045) 2px,transparent 2px);background-size:120px 120px}
#bgfx.glow{background:radial-gradient(600px 600px at 50% 50%,rgba(244,197,66,.10),transparent 70%)}
#subs{position:absolute;left:90px;right:150px;top:1300px;height:170px;display:flex;align-items:center;justify-content:center;text-align:center;flex-wrap:wrap;gap:0 18px;font-size:58px;font-weight:800;letter-spacing:-.02em;line-height:1.15;color:#F5F5F2;text-shadow:0 4px 18px rgba(0,0,0,.8)}
#subs .on{color:#F4C542}
body.has-subs .scene{padding-bottom:640px}
.w-word,.w-char{display:inline-block;white-space:pre}
"""

EXTRA_JS = """
window.__timelines = window.__timelines || {};
(function(){
  // palabra a palabra / letra a letra: partir el texto una vez
  for (const el of document.querySelectorAll('[data-a="words"],[data-a="type"]')) {
    const chars = el.dataset.a === 'type';
    const parts = chars ? [...el.textContent] : el.textContent.split(/(\\s+)/);
    el.innerHTML = parts.map(p => /^\\s+$/.test(p) ? p : `<span class="${chars?'w-char':'w-word'}" style="opacity:0">${p}</span>`).join('');
  }
  const base = window.setFrame;
  const ease = p => 1 - Math.pow(1 - p, 3);
  const back = p => { const c = 1.9; p -= 1; return 1 + (c + 1) * p * p * p + c * p * p; };
  window.setFrame = function(idx, t, dur, total, g, last){
    base(idx, t, dur, total, g, last);
    const s = __scenes[idx];
    for (const el of s.querySelectorAll('[data-in]')) {
      const a = el.dataset.a; if (!a) continue;
      const st = +el.dataset.in, d = +(el.dataset.d || 0.5), p = Math.max(0, Math.min(1, (t - st) / d)), e = ease(p);
      if (a === 'slide') { el.style.opacity = e; el.style.transform = `translateX(${(1-e)*160}px)`; }
      else if (a === 'left') { el.style.opacity = e; el.style.transform = `translateX(${-(1-e)*160}px)`; }
      else if (a === 'zoom') { el.style.opacity = e; el.style.transform = `scale(${1.35-0.35*e})`; }
      else if (a === 'stamp') { const b = back(p); el.style.opacity = Math.min(1, p*3); el.style.transform = `scale(${1.8-0.8*b}) rotate(${(1-e)*-6}deg)`; }
      else if (a === 'blur') { el.style.opacity = e; el.style.filter = `blur(${(1-e)*24}px)`; }
      else if (a === 'spin') { el.style.opacity = e; el.style.transform = `rotate(${(1-e)*-180}deg) scale(${0.5+0.5*e})`; }
      else if (a === 'hl') { el.style.backgroundSize = `${e*100}% ${el.closest('.news') ? 30 : 22}%`; }
      else if (a === 'kb') { const q = Math.max(0, Math.min(1, (t - st) / Math.max(0.1, dur - st))); el.style.opacity = Math.min(1, (t-st)/0.4); el.style.transform = `scale(${1.12 - 0.12*q})`; }
      else if (a === 'float') { el.style.opacity = Math.min(1, Math.max(0, (t-st)/0.4)); el.style.transform = `translateY(${Math.sin((t-st)*2.2)*12}px)`; }
      else if (a === 'shake') { const k = Math.max(0, 1 - Math.max(0, t - st) / d); el.style.opacity = t >= st ? 1 : 0; el.style.transform = `translateX(${Math.sin((t-st)*60)*18*k}px)`; }
      else if (a === 'words' || a === 'type') {
        const kids = el.children, n = kids.length, step = +(el.dataset.step || (a === 'type' ? 0.035 : 0.12));
        for (let k = 0; k < n; k++) { const q = Math.max(0, Math.min(1, (t - st - k*step) / (a === 'type' ? 0.01 : 0.25)));
          kids[k].style.opacity = q; if (a === 'words') kids[k].style.transform = `translateY(${(1-ease(q))*30}px)`; }
      }
    }
    for (const ph of s.querySelectorAll('.photo[data-kb] img')) { const q = Math.min(1, t / Math.max(0.1, dur)); ph.style.transform = `scale(${1.14 - 0.14*q})`; }
    // transiciones de salida (reel.py ya funde a negro en los últimos 0,3 s)
    const tr = s.dataset.trans || 'fade';
    if (!last && tr !== 'fade') {
      const k = Math.max(0, Math.min(1, (t - (dur - 0.3)) / 0.3)), q = k * k;
      if (tr === 'slide') s.style.transform = `translateX(${-q*260}px)`;
      else if (tr === 'zoom') s.style.transform = `scale(${1 + q*0.25})`;
      else if (tr === 'whip') { s.style.transform = `translateX(${-q*700}px)`; s.style.filter = `blur(${q*30}px)`; }
      else if (tr === 'cut') s.style.opacity = 1;
    }
    // entrada suave de cada escena
    if (idx > 0 && t < 0.25 && tr !== 'cut') { const k = ease(t / 0.25); s.style.transform = `scale(${1.04 - 0.04*k})`; }
    else if (!(t > dur - 0.3 && tr !== 'fade')) s.style.transform = '';
    const tl = window.__timelines['s' + idx]; if (tl) tl.seek(t, false);
    const bg = document.getElementById('bgfx');
    if (bg) bg.style.transform = `translate(${(g*14)%120}px, ${(g*9)%120}px) scale(${1 + 0.02*Math.sin(g*0.6)})`;
    if (window.__subs) {
      const box = document.getElementById('subs'), W = window.__subs[idx] || [];
      let cur = -1; for (let k = 0; k < W.length; k++) if (t >= W[k][1]) cur = k;
      if (cur < 0 || t > W[W.length-1][2] + 0.6) { box.innerHTML = ''; }
      else { const c0 = Math.floor(cur / 4) * 4;
        box.innerHTML = W.slice(c0, c0 + 4).map((w, k) => `<span class="${c0+k===cur?'on':''}">${w[0]}</span>`).join(' '); }
    }
  };
})();
"""

def _icon_svg(ref):
    lib, name = ref.split(":", 1)
    if lib == "lucide":
        f = NM / "lucide-static" / "icons" / f"{name}.svg"
    elif lib == "si":
        f = NM / "simple-icons" / "icons" / f"{name}.svg"
    else:
        raise SystemExit(f"Icono desconocido: {ref} (usa lucide:<nombre> o si:<marca>)")
    if not f.exists():
        raise SystemExit(f"No existe el icono {ref} ({f}). ¿Has hecho `npm ci` en la raíz del repo?")
    svg = f.read_text(encoding="utf-8")
    svg = re.sub(r'<!--.*?-->', '', svg, flags=re.S)
    svg = re.sub(r'\s(width|height)="[^"]*"', '', svg, count=2)
    if lib == "si":
        svg = svg.replace("<svg ", '<svg fill="currentColor" ', 1)
    return svg

def _fmt(v, dec=0):
    s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def _chart(cfg):
    typ = cfg.get("type", "line"); data = [float(x) for x in cfg["data"]]
    Wd, Hd = cfg.get("w", 840), cfg.get("h", 520); t0 = float(cfg.get("in", 0.3)); d = float(cfg.get("d", 1.4))
    unit = cfg.get("unit", ""); dec = int(cfg.get("dec", 0)); col = cfg.get("color", "#F4C542")
    labels = cfg.get("labels", []); sfx = cfg.get("sfx")
    pad_t, pad_b = 70, 60
    sf = f' data-sfx="{sfx}"' if sfx else ""
    if typ == "bar":
        n = len(data); gap = Wd / n; bw = gap * 0.62; mx = max(data) or 1
        out = []
        colors = cfg.get("colors"); mark = cfg.get("mark")
        for i, v in enumerate(data):
            h = (Hd - pad_t - pad_b) * v / mx; x = i * gap + (gap - bw) / 2; y = Hd - pad_b - h
            c = (colors[i] if colors else ("#F4C542" if mark is None or (mark % n) == i else "#5E5E5A"))
            st = t0 + i * (d / max(1, n))
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="10" fill="{c}" data-in="{st:.2f}" data-d="0.55" data-a="growy"{sf if i == 0 else ""}/>')
            out.append(f'<text x="{x+bw/2:.0f}" y="{y-16:.0f}" fill="#F5F5F2" font-size="38" font-weight="800" text-anchor="middle" data-in="{st+0.35:.2f}" data-a="fade">{_fmt(v, dec)}{_html.escape(unit)}</text>')
            if i < len(labels):
                out.append(f'<text x="{x+bw/2:.0f}" y="{Hd-14}" fill="#CFCFCA" font-size="28" text-anchor="middle">{_html.escape(str(labels[i]))}</text>')
        return f'<svg viewBox="0 0 {Wd} {Hd}" width="{Wd}" style="overflow:visible">{"".join(out)}</svg>'
    lo = float(cfg.get("min", min(data))); hi = float(cfg.get("max", max(data))); rng = (hi - lo) or 1
    pts = [(i * Wd / (len(data) - 1), pad_t + (Hd - pad_t - pad_b) * (1 - (v - lo) / rng)) for i, v in enumerate(data)]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = path + f" L{Wd},{Hd-pad_b} L0,{Hd-pad_b} Z"
    mk = cfg.get("mark", -1); mx_, my_ = pts[mk]
    lab = []
    for i, l in enumerate(labels):
        x = i * Wd / max(1, len(labels) - 1)
        anc = "start" if i == 0 else ("end" if i == len(labels) - 1 else "middle")
        lab.append(f'<text x="{x:.0f}" y="{Hd-12}" fill="#CFCFCA" font-size="28" text-anchor="{anc}">{_html.escape(str(l))}</text>')
    vt = cfg.get("mark_label", f"{_fmt(data[mk], dec)}{unit}")
    anc = "end" if mx_ > Wd * 0.6 else "start"; dx = -28 if anc == "end" else 28
    gid = f"ga{abs(hash(path)) % 99999}"
    return (f'<svg viewBox="0 0 {Wd} {Hd}" width="{Wd}" style="overflow:visible">'
            f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".28"/>'
            f'<stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
            f'<line x1="0" y1="{Hd-pad_b}" x2="{Wd}" y2="{Hd-pad_b}" stroke="#2E2E2B" stroke-width="3"/>'
            f'<path d="{area}" fill="url(#{gid})" data-in="{t0+d*0.6:.2f}" data-d="0.6" data-a="fade"/>'
            f'<path d="{path}" fill="none" stroke="{col}" stroke-width="8" stroke-linejoin="round" stroke-linecap="round" data-in="{t0:.2f}" data-d="{d:.2f}" data-a="draw"{sf}{f' data-sfx-at="{d:.2f}"' if sfx else ""}/>'
            f'<circle cx="{mx_:.1f}" cy="{my_:.1f}" r="16" fill="{col}" data-in="{t0+d:.2f}" data-d="0.35" data-a="pop"/>'
            f'<text x="{mx_+dx:.0f}" y="{my_-44:.0f}" fill="#F5F5F2" font-size="44" font-weight="800" text-anchor="{anc}" data-in="{t0+d+0.1:.2f}" data-a="fade">{_html.escape(vt)}</text>'
            f'{"".join(lab)}</svg>')

def _news(cfg):
    t0 = float(cfg.get("in", 0.2)); sfx = cfg.get("sfx", "paper")
    tit = _html.escape(cfg["titular"])
    k = [0]
    def hl(m):
        k[0] += 1
        return f'<span class="hl" data-in="{t0 + 0.6 + 0.25*k[0]:.2f}" data-d="0.45" data-a="hl">{m.group(1)}</span>'
    tit = re.sub(r"\*\*(.+?)\*\*", hl, tit)
    q = f'<div class="nq">{_html.escape(cfg["nota"])}</div>' if cfg.get("nota") else ""
    return (f'<div class="news" data-in="{t0:.2f}" data-d="0.5" data-a="{cfg.get("a","slide")}" data-sfx="{sfx}">'
            f'<div class="nm">{_html.escape(cfg["medio"])}<span>{_html.escape(cfg.get("fecha",""))}</span></div>'
            f'<div class="nt">{tit}</div>{q}</div>')

CUR_SLUG = None

def _auto_credit(src):
    f = ROOT / "posts" / (CUR_SLUG or "") / "assets" / "creditos.json"
    if CUR_SLUG and f.exists():
        cr = json.loads(f.read_text(encoding="utf-8")).get(pathlib.Path(src).stem)
        if cr: return cr.get("credito", "")
    return ""

def _photo(cfg):
    t0 = float(cfg.get("in", 0.1)); h = int(cfg.get("h", 760)); sfx = cfg.get("sfx", "camera")
    if cfg.get("credito") == "auto":
        cfg = {**cfg, "credito": _auto_credit(cfg["src"])}
    cr = f'<div class="cr">{_html.escape(cfg["credito"])}</div>' if cfg.get("credito") else ""
    pos = cfg.get("pos", "50% 40%")
    return (f'<div class="photo" data-kb style="height:{h}px" data-in="{t0:.2f}" data-d="0.5" data-a="{cfg.get("a","zoom")}" data-sfx="{sfx}">'
            f'<img src="{_html.escape(cfg["src"])}" style="object-position:{pos}">{cr}</div>')

def expand(h):
    def icon(m):
        tag = m.group(0); a = {k: (v1 or v2) for k, v1, v2 in re.findall(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')', tag)}
        size = a.pop("data-size", "120"); ref = a.pop("data-icon")
        style = f'width:{size}px;height:{size}px;' + a.pop("style", "")
        cls = "icon " + a.pop("class", "")
        rest = "".join(f' {k}="{_html.escape(v)}"' for k, v in a.items())
        return f'<span class="{cls.strip()}" style="{style}"{rest}>{_icon_svg(ref)}</span>'
    h = re.sub(r'<i\s[^>]*data-icon=[^>]*>\s*</i>', icon, h)
    for key, fn in (("data-chart", _chart), ("data-news", _news), ("data-photo", _photo)):
        def rep(m, key=key, fn=fn):
            attrs = m.group(1); raw = re.search(key + r"='([^']*)'", attrs)
            cfg = json.loads(raw.group(1)); rest = attrs.replace(raw.group(0), "").strip()
            return f'<div {rest}>{fn(cfg)}</div>' if rest else fn(cfg)
        h = re.sub(r"<div\s([^>]*" + key + r"='[^']*'[^>]*)>\s*</div>", rep, h)
    return h

def head(spec, slug):
    base = (ROOT / "posts" / slug).as_uri() + "/"
    js = ""
    for f in ("gsap.min.js", "SplitText.min.js", "TextPlugin.min.js", "DrawSVGPlugin.min.js", "MorphSVGPlugin.min.js", "CustomEase.min.js"):
        p = NM / "gsap" / "dist" / f
        if p.exists():
            js += f'<script src="{p.as_uri()}"></script>'
    js += ("<script>window.__timelines={};window.TL=function(i){const tl=gsap.timeline({paused:true});"
           "window.__timelines['s'+i]=tl;return tl;};if(window.gsap){for(const n of ['SplitText','TextPlugin',"
           "'DrawSVGPlugin','MorphSVGPlugin','CustomEase'])if(window[n])gsap.registerPlugin(window[n]);}</script>")
    return f'<base href="{base}"><style>{EXTRA_CSS}</style>{js}'

def body_before(spec):
    fondo = spec.get("fondo", "grid")
    return f'<div id="bgfx" class="{fondo}"></div>' if fondo in ("grid", "glow") else ""

def body_after(spec):
    return '<div id="subs"></div>' if spec.get("subtitulos") else ""

def scene_attrs(sc):
    return f' data-trans="{sc["trans"]}"' if sc.get("trans") else ""

def _syl(w):
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", w.lower())))

def subs_timing(scenes, voice_durs, lead):
    """Reparte cada palabra de "voz" en el tiempo de su clip, en proporción a sus sílabas (y pausas en la puntuación)."""
    out = []
    for sc, vd in zip(scenes, voice_durs):
        words = (sc.get("voz") or "").split()
        if not words or not vd:
            out.append([]); continue
        wts = [_syl(w) + (1.2 if w[-1] in ".?!" else 0.5 if w[-1] in ",:;…" else 0) for w in words]
        tot = sum(wts); t = lead; row = []
        for w, k in zip(words, wts):
            d = vd * k / tot; row.append([_html.escape(w), round(t, 3), round(t + d, 3)]); t += d
        out.append(row)
    return out

def subs_script(timing):
    return f"<script>window.__subs={json.dumps(timing, ensure_ascii=False)};document.body.classList.add('has-subs');</script>"

VOL = {"tick": 0.35, "type": 0.45, "pop": 0.6, "click": 0.6, "whoosh": 0.55, "swoosh": 0.5, "impact": 0.6,
       "riser": 0.5, "cash": 0.6, "coin": 0.6, "ding": 0.55, "glitch": 0.5, "error": 0.6, "success": 0.6,
       "camera": 0.55, "paper": 0.6}

def cues(spec, starts, durs):
    out = []
    for i, (sc, st) in enumerate(zip(spec["scenes"], starts)):
        h = expand(sc.get("html", ""))
        for tag in re.findall(r"<[^>]*data-sfx=[^>]*>", h):
            a = {k: (v1 or v2) for k, v1, v2 in re.findall(r'([\w-]+)=(?:"([^"]*)"|\'([^\']*)\')', tag)}
            if a.get("data-sfx") and "data-in" in a:
                out.append({"t": round(st + float(a["data-in"]) + float(a.get("data-sfx-at", 0.05)), 3), "s": a["data-sfx"],
                            "v": float(a.get("data-sfx-v", 1)), "escena": i})
        for c in sc.get("sfx", []):
            out.append({"t": round(st + float(c["t"]), 3), "s": c["s"], "v": float(c.get("v", 1)), "escena": i})
        if i > 0 and spec.get("sfx_transiciones", True) and sc.get("trans", "fade") != "cut":
            out.append({"t": round(st - 0.05, 3), "s": "whoosh", "v": 0.45, "escena": i})
    return sorted(out, key=lambda c: c["t"])

_cache = {}
def _load(name):
    if name not in _cache:
        f = SFX_DIR / f"{name}.wav"
        if not f.exists():
            print(f"  aviso: no existe generator/sfx/{name}.wav, se omite"); _cache[name] = None
        else:
            import soundfile as sf
            a, sr = sf.read(str(f), dtype="float32", always_2d=True); a = a.mean(axis=1)
            if sr != SR:
                a = np.interp(np.linspace(0, len(a) - 1, int(len(a) * SR / sr)), np.arange(len(a)), a).astype(np.float32)
            env = np.convolve(np.abs(a), np.ones(240) / 240, mode="same")
            _cache[name] = (a / max(1e-9, np.abs(a).max()), int(env.argmax()))
    return _cache[name]

def sfx_track(cs, total, gain=0.32):
    tr = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for c in cs:
        got = _load(c["s"])
        if got is None: continue
        a, pk = got
        p0 = int(c["t"] * SR) - pk
        if p0 < 0: a = a[-p0:]; p0 = 0
        n = min(len(a), len(tr) - p0)
        if n > 0: tr[p0:p0 + n] += a[:n] * VOL.get(c["s"], 0.6) * c.get("v", 1) * gain
    return tr
