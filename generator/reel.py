#!/usr/bin/env python3
"""Renderiza un Reel de Capital Sin Filtros (1080x1920, 30 fps, H.264 + AAC) desde un spec JSON.

Uso:
  python3 generator/reel.py generator/specs/<slug>.json [--frames t1,t2,...]
    --frames: solo dibuja fotogramas sueltos (segundos globales) en generator/.frames/ para revisarlos.
Salida: posts/<slug>/reel.mp4 y posts/<slug>/cover.jpg

Spec:
{ "slug": "...", "music_seed": 3, "voice": "davefx",
  "scenes": [ {"dur": 3.5, "voz": "Texto que lee la voz en off.", "html": "<div ...>"} , ... ] }
Voz en off (Piper, local y gratis): si una escena tiene "voz", la escena dura lo que tarde la voz + 0,7 s
(o "dur" si es mayor). "voice_speed" (por defecto 0.9; menor = más rápido). Duración orientativa: 30-50 s; prioriza el contenido
completo antes que recortar segundos. Escribe los números EN LETRAS en "voz" ("trescientos cinco mil euros").
Voces: "csf" (POR DEFECTO, voz oficial clonada desde voices/csf_voz_oficial.wav con Qwen3-TTS; "voice_speed" 1.0)
  | "kokoro:em_alex" (masculina, dinámica) | "kokoro:em_santa" | "kokoro:ef_dora" (femenina)
  -> Kokoro, Apache 2.0, requiere `pip install kokoro-onnx`; "voice_speed" por defecto 1.05 (mayor = más rápido).
  Piper (más plano): "davefx" (CC0) | "sharvard-m" / "sharvard-f" (CC BY 3.0, requiere atribución); speed 0.9 (menor = más rápido).
Tono del guion: dinámico y cercano (preguntas, frases cortas, alguna exclamación), sin hype ni primera persona.
Los modelos se descargan de Hugging Face a ~/.cache/csf-voices la primera vez.

Cada escena es HTML libre dentro de un lienzo de 1080x1920 con la marca aplicada (clases como en los
carruseles: .k kicker, h1, h2, p, .big, .lab, .g dorado, .src fuente). Zona segura: el contenido debe
quedar entre y=260 y y=1480 y x=90..930 (Instagram tapa abajo y a la derecha).
Animación por atributos (tiempos en segundos desde el inicio de la escena):
  data-in="0.4"  data-d="0.6"  data-a="up|fade|pop|grow|growy|draw|count"
  count: data-to="305000" data-suf=" €" (formato español con puntos)
  draw:  en <path>, dibuja el trazo;  grow/growy: barras (escala desde izquierda/abajo)
Cada escena se funde a negro en sus últimos 0,3 s (salvo la última).
"""
import json, sys, pathlib, subprocess, os, shutil, wave, urllib.request
import numpy as np

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

VOICES = {"davefx": ("davefx", 0), "sharvard-m": ("sharvard", 0), "sharvard-f": ("sharvard", 1)}
SR = 48000

def voice_model(name):
    v, spk = VOICES[name]
    d = pathlib.Path.home() / ".cache" / "csf-voices"; d.mkdir(parents=True, exist_ok=True)
    base = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/{v}/medium/es_ES-{v}-medium"
    for ext in ("onnx", "onnx.json"):
        f = d / f"es_ES-{v}-medium.{ext}"
        if not f.exists():
            urllib.request.urlretrieve(f"{base}.{ext}", f)
    return d / f"es_ES-{v}-medium.onnx", spk

KOKORO = "https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX/resolve/main"
_kok = {}

def kokoro_synth(text, voice, speed):
    """Kokoro (Apache 2.0): voces más naturales y expresivas. Requiere `pip install kokoro-onnx`."""
    d = pathlib.Path.home() / ".cache" / "csf-voices" / "kokoro"; d.mkdir(parents=True, exist_ok=True)
    if not (d / "model.onnx").exists():
        urllib.request.urlretrieve(f"{KOKORO}/onnx/model.onnx", d / "model.onnx")
    vf = d / f"{voice}.bin"
    if not vf.exists():
        urllib.request.urlretrieve(f"{KOKORO}/voices/{voice}.bin", vf)
    if voice not in _kok:
        from kokoro_onnx import Kokoro
        npz = d / f"v_{voice}.npz"
        np.savez(npz, **{voice: np.fromfile(vf, dtype=np.float32).reshape(-1, 1, 256)})
        _kok[voice] = Kokoro(str(d / "model.onnx"), str(npz))
    a, sr = _kok[voice].create(text, voice=voice, speed=speed, lang="es")
    a = np.asarray(a, dtype=np.float32)
    return np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)

_qwen = {}

def qwen_clone_synth(texts, speed=1.0):
    """Clona la voz oficial (voices/csf_voz_oficial.*) con Qwen3-TTS Base. Lento en CPU (~5 s por s de audio).
    Requiere `pip install qwen-tts` y descargar el modelo de Hugging Face (usar HF_HUB_DISABLE_XET=1)."""
    import torch
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    from qwen_tts import Qwen3TTSModel
    if "m" not in _qwen:
        torch.set_num_threads(max(1, os.cpu_count() or 1))
        _qwen["m"] = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.bfloat16)
        ref = ROOT / "voices" / "csf_voz_oficial.wav"
        _qwen["p"] = _qwen["m"].create_voice_clone_prompt(str(ref), (ROOT / "voices" / "csf_voz_oficial.txt").read_text(encoding="utf-8"))
    out = []
    for t in texts:
        wavs, sr = _qwen["m"].generate_voice_clone(text=t, language="Spanish", voice_clone_prompt=_qwen["p"])
        a = np.asarray(wavs[0], dtype=np.float32)
        if speed != 1.0:
            tmp_in, tmp_out = ROOT / "generator" / ".q_in.wav", ROOT / "generator" / ".q_out.wav"
            with wave.open(str(tmp_in), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(tmp_in), "-af", f"rubberband=tempo={speed}", str(tmp_out)], check=True)
            with wave.open(str(tmp_out)) as w:
                a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        out.append(np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a))
    return out

def synth(text, model, spk, out, speed=0.9):
    subprocess.run([sys.executable, "-m", "piper", "-m", str(model), "-s", str(spk), "--length-scale", str(speed), "--sentence-silence", "0.2", "-f", str(out)],
                   input=text.encode(), check=True, capture_output=True)
    with wave.open(str(out)) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if sr != SR:
        a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a

def build_html(spec):
    scenes = "".join(f'<div class="scene">{sc["html"]}</div>' for sc in spec["scenes"])
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>'
            f'<div id="bar"></div><div id="logo">CSF</div>{scenes}<script>{JS}</script></body></html>')

def main():
    spec_path = pathlib.Path(sys.argv[1]); spec = json.loads(spec_path.read_text(encoding="utf-8"))
    slug = spec["slug"]; scenes = spec["scenes"]
    gen0 = ROOT / "generator" / ".reel_voice"; shutil.rmtree(gen0, ignore_errors=True); gen0.mkdir(parents=True)
    clips = []
    vname = spec.get("voice", "csf")
    if any(sc.get("voz") for sc in scenes):
        if vname == "csf":
            idx = [i for i, sc in enumerate(scenes) if sc.get("voz")]
            gen_ = qwen_clone_synth([scenes[i]["voz"] for i in idx], spec.get("voice_speed", 1.0))
            clips = [None] * len(scenes)
            for i, c in zip(idx, gen_): clips[i] = c
        elif vname.startswith("kokoro:"):
            kv = vname.split(":", 1)[1]
            for sc in scenes:
                clips.append(kokoro_synth(sc["voz"], kv, spec.get("voice_speed", 1.05)) if sc.get("voz") else None)
        else:
            model, spk = voice_model(vname)
            for i, sc in enumerate(scenes):
                clips.append(synth(sc["voz"], model, spk, gen0 / f"v{i}.wav", spec.get("voice_speed", 0.9)) if sc.get("voz") else None)
    else:
        clips = [None] * len(scenes)
    LEAD = 0.2
    durs = [max(float(sc.get("dur", 0)), (len(c) / SR + LEAD + 0.5) if c is not None else 0) for sc, c in zip(scenes, clips)]
    durs = [round(d * FPS) / FPS for d in durs]; total = sum(durs)
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
    has_voice = any(c is not None for c in clips)
    final_tmp = out / "reel.part.mp4"
    if has_voice:
        vt = np.zeros(int(total * SR) + SR, dtype=np.float32)
        for st, c in zip(starts, clips):
            if c is None: continue
            a = int((st + LEAD) * SR); vt[a:a + len(c)] += c[: len(vt) - a]
        vt = vt / max(1e-9, np.abs(vt).max()) * 0.9
        vw = tmp / "voice.wav"
        with wave.open(str(vw), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((vt * 32767).astype(np.int16).tobytes())
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav), "-i", str(vw),
               "-filter_complex", "[1:a]volume=0.22[m];[2:a]aformat=channel_layouts=stereo,volume=1.0[v];[m][v]amix=inputs=2:duration=first:normalize=0[a]",
               "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest",
               "-movflags", "+faststart", str(final_tmp)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(final_tmp)]
    subprocess.run(cmd, check=True)
    final_tmp.rename(out / "reel.mp4"); shutil.rmtree(tmp, ignore_errors=True)
    mb = (out / "reel.mp4").stat().st_size / 1e6
    print(f"OK posts/{slug}/reel.mp4 ({total:.1f}s, {mb:.1f} MB) + cover.jpg")

if __name__ == "__main__":
    main()
