# Seguridad de las skills (NVIDIA SkillSpector)

Desde el 25-11-2026 (decisión de Pol) toda skill nueva se escanea **antes** de instalarla.

## Herramientas
- **SkillSpector** (NVIDIA, Apache 2.0, `NVIDIA/skillspector`, fijado a `0205488`): escáner estático de skills
  (71 patrones: inyección de prompt, exfiltración, escalada de privilegios, cadena de suministro, YARA...).
- **Skill `skill-inspector`** (`.claude/skills/skill-inspector`, del mismo repo): procedimiento para revisar una skill
  combinando el informe de SkillSpector con una revisión semántica (intención, permisos, comportamiento oculto).
- `tools/scan_skills.py <carpeta>`: lanza SkillSpector (`--no-llm`) sobre una skill o todas y resume.
  Ignora AE1 (referencia que el parser no leyó entera) y PE3 (el texto menciona una API key o un `.env`), que en
  skills de documentación son falsos positivos, y las huellas ya revisadas de `tools/skills_revisadas.json`.
  Sale con error si queda algo grave sin revisar.
- Workflow `.github/workflows/scan-skills.yml`: se ejecuta solo al cambiar `.claude/skills/**` (y a mano);
  deja el informe como artefacto `informe-skillspector`.

## Cómo instalar una skill nueva
1. Descárgala a una carpeta temporal (nunca directamente a `.claude/skills`).
2. `pip install "git+https://github.com/NVIDIA/skillspector.git@0205488a8257869cac3054397ddd5a5d29180aab"` en un venv
   y `python3 tools/scan_skills.py <carpeta>`.
3. Lee los hallazgos graves uno a uno (`skillspector scan <carpeta> --no-llm`). Un "SAFE" no es garantía (Checkmarx
   mostró skills maliciosas con "SAFE") y un "DO_NOT_INSTALL" puede ser un falso positivo: decide leyendo el código.
4. Solo entonces cópiala a `.claude/skills/`, añádela a `skills-lock.json` (repo, commit, hash) y, si tenía
   hallazgos revisados, sus huellas a `tools/skills_revisadas.json`.

## Revisión del 25-11-2026 (37 skills)
- Sin hallazgos graves reales. Los "CRITICAL/DO_NOT_INSTALL" de hyperframes, media-use, real-sfx, remotion-* y
  slideshow venían de AE1/PE3 (documentación que habla de tokens de Mapbox, HeyGen, AWS...) y de 12 hallazgos
  revisados a mano: comentarios HTML en plantillas de subtítulos (P2), código de tests que simula llamadas DELETE
  (TM1), una lectura de archivo propio en `critique.py` (TT1), frases de documentación (AR2, P6).
- `media-use` puede leer claves de HeyGen/ElevenLabs/Gemini de un `.env` si existen: aquí no hay ninguno y no se usa.
- **Agent Reach** (`Panniantong/Agent-Reach`, `8d9ecc1`): instalada **solo la skill** (`SKILL.md` + referencias,
  SkillSpector: SAFE, 0). El CLI completo (`pip install agent-reach`) da CRITICAL porque reutiliza sesiones y cookies
  del navegador para entrar en redes con tu cuenta (PE3/SSRF/TT3 en `runtime/browser.py`): **no se instala** el CLI
  con cuentas ni cookies. Si algún día hace falta, solo canales públicos sin login y en un entorno sin datos personales.
  Además, este entorno no tiene salida a YouTube/Instagram/TikTok/Reddit: la investigación se hace con la búsqueda web.
