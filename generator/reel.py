#!/usr/bin/env python3
"""Renderiza un Reel de Capital Sin Filtros (1080x1920, 30 fps, H.264 + AAC) desde un spec JSON.

Uso:
  python3 generator/reel.py generator/specs/<slug>.json [--frames t1,t2,...]
    --frames: solo dibuja fotogramas sueltos (segundos globales) en generator/.frames/ para revisarlos.
Salida: posts/<slug>/reel.mp4 y posts/<slug>/cover.jpg

Spec:
{ "slug": "...", "music_seed": 3,
  "scenes": [ {"dur": 3.5, "html": "<div ...>"} , ... ] }

Cada escena es HTML libre dentro de un lienzo de 1080x1920 con la marca aplicada (clases como en los
carruseles: .k kicker, h1, h2, p, .big, .lab, .g dorado, .src fuente). Zona segura: el contenido debe
quedar entre y=260 y y=1480 y x=90..930 (Instagram tapa abajo y a la derecha).
Animación por atributos (tiempos en segundos desde el inicio de la escena):
  data-in="0.4"  data-d="0.6"  data-a="up|fade|pop|grow|growy|draw|count"
  count: data-to="305000" data-suf=" €" (formato español con puntos)
  draw:  en <path>, dibuja el trazo;  grow/growy: barras (escala desde izquierda/abajo)
Cada escena se funde a negro en sus últimos 0,3 s (salvo la última).
"""
import json, sys, pathlib, subprocess, os, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
FPS = 30
W, H = 1080, 1920

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1920px;background:#0A0A0A;overflow:hidden;font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased;color:#F5F5F2}
.scene{position:absolute;inset:0;padding:300px 90px 440px 90px;display:none;flex-direction:column;justify-content:center}
.scene.on{display:flex}
#bar{position:absolute;top:0;left:0;height:10px;background:#F4C542;width:0}
#logo{position:absolute;top:150px;left:90px;font-weight:800;font-size:40px;color:#F4C542;letter-spacing:.02em}
.k{font-size:36px;font-weight:600;color:#F4C542;letter-spacing:.12em;text-transform:uppercase;margin-bottom:40px}
h1{font-size:104px;line-height:1.04;font-weight:800;letter-spacing:-.035em}
h2{font-size:84px;line-height:1.08;font-weight:800;letter-spacing:-.03em}
p{font-size:46px;line-height:1.36;color:#CFCFCA;margin-top:40px}
b{color:#F5F5F2}.g{color:#F4C542}
.big{white-space:nowrap;font-size:176px;font-weight:800;letter-spacing:-.05em;line-height:1;color:#F4C542;margin:24px 0 10px}
.lab{font-size:44px;font-weight:500;color:#CFCFCA}
.src{font-size:28px;color:#6F6F6F;line-height:1.4;margin-top:36px}
svg{display:block}
[data-in]{will-change:opacity,transform}
"""

JS = """
window.__scenes=[...document.querySelectorAll('.scene')];
for (const p of document.querySelectorAll('path[data-a="draw"]')) { p.__len = p.getTotalLength(); p.style.strokeDasharray = p.__len; }
function fmt(v){ return Math.round(v).toString().replace(/\\B(?=(\\d{3})+(?!\\d))/g,'.'); }
window.setFrame = function(idx, t, dur, total, globalT, last){
  __scenes.forEach((s,i)=>s.classList.toggle('on', i===idx));
  const s = __scenes[idx];
  document.getElementById('bar').style.width = (100*globalT/total)+'%';
  for (const el of s.querySelectorAll('[data-in]')) {
    const st=+el.dataset.in, d=+(el.dataset.d||0.5), a=el.dataset.a||'up';
    const p=Math.max(0,Math.min(1,(t-st)/d)), e=1-Math.pow(1-p,3);
    if (a==='up'){ el.style.opacity=e; el.style.transform=`translateY(${(1-e)*50}px)`; }
    else if (a==='fade'){ el.style.opacity=e; }
    else if (a==='pop'){ el.style.opacity=e; el.style.transform=`scale(${0.6+0.4*e})`; el.style.transformOrigin='center'; el.style.transformBox='fill-box'; }
    else if (a==='grow'){ el.style.transform=`scaleX(${e})`; el.style.transformOrigin='left center'; el.style.transformBox='fill-box'; }
    else if (a==='growy'){ el.style.transform=`scaleY(${e})`; el.style.transformOrigin='center bottom'; el.style.transformBox='fill-box'; }
    else if (a==='draw'){ el.style.strokeDashoffset = el.__len*(1-e); }
    else if (a==='count'){ el.textContent = fmt((+el.dataset.to)*e) + (el.dataset.suf||''); }
  }
  const fo = last ? 1 : Math.max(0, Math.min(1, (dur - t)/0.3));
  s.style.opacity = fo;
}
"""

def build_html(spec):
    scenes = "".join(f'<div class="scene">{sc["html"]}</div>' for sc in spec["scenes"])
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div id="bar"></div><div id="logo">CSF</div>{scenes}<script>{JS}</script></body></html>')

def main():
    spec_path = pathlib.Path(sys.argv[1]); spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slug = spec["slug"]; scenes = spec["scenes"]
    durs = [float(s["dur"]) for s in scenes]; total = sum(durs)
    if not 3 <= total <= 90:
        sys.exit("Un Reel debe durar entre 3 y 90 s (recomendado 15-30 s).")
    gen = ROOT / "generator"; html = gen / ".reel.html"; html.write_text(build_html(spec), encoding="utf-8")
    frames_only = None
    if "--frames" in sys.argv:
        frames_only = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
    from playwright.sync_api import sync_playwright
    out = ROOT / "posts" / slug; out.mkdir(parents=True, exist_ok=True)
    tmp = gen / ".reel_tmp"; shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
    starts = [sum(durs[:i]) for i in range(len(durs))]
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(html.as_uri()); pg.evaluate("document.fonts.ready")
        def draw(i, t):
            last = i == len(scenes) - 1
            pg.evaluate(f"setFrame({i},{t},{durs[i]},{total},{starts[i]+t},{str(last).lower()})")
            return pg.screenshot(type="jpeg", quality=92)
        if frames_only is not None:
            fd = gen / ".frames"; shutil.rmtree(fd, ignore_errors=True); fd.mkdir()
            for g in frames_only:
                i = max(k for k in range(len(starts)) if starts[k] <= g)
                (fd / f"f_{g:05.2f}.jpg").write_bytes(draw(i, g - starts[i]))
            print(f"Fotogramas en {fd}"); b.close(); return
        parts = []
        for i, d in enumerate(durs):
            n = round(d * FPS); part = tmp / f"s{i:02d}.part.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                                   "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                                   "-maxrate", "5M", "-bufsize", "10M", "-pix_fmt", "yuv420p", "-r", str(FPS),
                                   "-g", str(FPS * 2), str(part)], stdin=subprocess.PIPE)
            for f in range(n):
                ff.stdin.write(draw(i, f / FPS))
            ff.stdin.close()
            if ff.wait() != 0: sys.exit(f"ffmpeg falló en la escena {i}")
            final = tmp / f"s{i:02d}.mp4"; part.rename(final); parts.append(final)
            if i == 0:
                pg.evaluate(f"setFrame(0,{min(d-0.35, 2.0)},{d},{total},1,false)")
                pg.screenshot(path=str(out / "cover.jpg"), type="jpeg", quality=92)
        b.close()
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    video = tmp / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(video)], check=True)
    wav = tmp / "music.wav"
    subprocess.run([sys.executable, str(gen / "music.py"), str(total), str(wav), "--seed", str(spec.get("music_seed", 1))], check=True)
    final_tmp = out / "reel.part.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
                    str(final_tmp)], check=True)
    final_tmp.rename(out / "reel.mp4"); shutil.rmtree(tmp, ignore_errors=True)
    mb = (out / "reel.mp4").stat().st_size / 1e6
    print(f"OK posts/{slug}/reel.mp4 ({total:.1f}s, {mb:.1f} MB) + cover.jpg")

if __name__ == "__main__":
    main()
