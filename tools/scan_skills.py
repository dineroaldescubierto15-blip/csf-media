#!/usr/bin/env python3
"""Escanea skills con NVIDIA SkillSpector (estático, --no-llm) y resume el riesgo real.

Uso: python3 tools/scan_skills.py [.claude/skills | .claude/skills/<skill>] [carpeta_informe]

SkillSpector marca como HIGH cosas que suelen ser inofensivas en skills de documentación
(AE1: referencia que el parser no pudo leer entera; PE3: el texto menciona una API key o un .env).
Este script separa esas categorías del resto y falla (exit 1) solo si aparece algo de las
categorías que sí indican peligro (inyección de prompt, exfiltración, ejecución de código,
YARA, cadena de suministro...) con severidad HIGH o CRITICAL. Una skill nueva no se instala
sin revisar a mano su informe (ver docs/seguridad-skills.md).
"""
import json, pathlib, subprocess, sys, collections

BENIGNAS = {"AE1", "PE3"}          # revisadas el 25-11-2026: falsos positivos en skills de docs
REVISADAS = set(json.loads((pathlib.Path(__file__).parent / "skills_revisadas.json").read_text())["huellas"])
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".claude/skills")
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "informe"); out.mkdir(exist_ok=True)
dirs = [root] if (root / "SKILL.md").exists() else sorted(p for p in root.iterdir() if (p / "SKILL.md").exists())
peligro, filas = [], []
for d in dirs:
    rep = out / f"{d.name}.json"
    subprocess.run(["skillspector", "scan", str(d), "--no-llm", "--format", "json", "--output", str(rep)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not rep.exists():
        filas.append(f"| {d.name} | ? | no se pudo escanear |"); peligro.append(d.name); continue
    r = json.loads(rep.read_text())
    graves = [i for i in r.get("issues", []) if i["severity"] in ("HIGH", "CRITICAL")]
    reales = [i for i in graves if i["id"] not in BENIGNAS and i.get("match_fingerprint") not in REVISADAS]
    c = collections.Counter(i["id"] for i in reales)
    filas.append(f"| {d.name} | {r['risk_assessment']['score']} | {r['risk_assessment']['recommendation']} | "
                 f"{', '.join(f'{k}×{v}' for k, v in c.items()) or '-'} |")
    if reales: peligro.append(d.name)
md = "| skill | score | SkillSpector | hallazgos graves a revisar |\n|---|---|---|---|\n" + "\n".join(filas)
(out / "resumen.md").write_text(md + "\n"); print(md)
if peligro:
    print("\nRevisar a mano:", ", ".join(peligro)); sys.exit(1)
