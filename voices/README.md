# Voz oficial de Capital Sin Filtros

Voz oficial ("csf") desde el 20-11-2026: **`csf_voz_oficial.pt`**, perfil de clonación de Qwen3-TTS
(`create_voice_clone_prompt`, modo ICL) que `generator/reel.py` carga directamente con
`torch.load(..., weights_only=True)`. Se usa con el modelo `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (no es compatible con el 0.6B).

- Origen: voz masculina **sintética y original** (~30 años, castellano peninsular con distinción /θ/), creada por Pol con
  Qwen3-TTS VoiceDesign. No deriva de ninguna grabación de una persona real.
- Estilo "Pro_Enfasis": profesional de finanzas, con énfasis en cifras. Parámetros de generación en `QWEN_GEN` (reel.py).
- Ficha completa (diseño, filtros, parámetros, validación, hash del perfil): `csf_voz_oficial_config.json`.
- Modelo en float32 (en bfloat16 suena más robótica). Por escena se generan 2 tomas (`"voice_takes"`) y se elige la de
  más entonación y menos duración; luego se acortan los silencios entre frases (máx. 0,22 s) y se acelera un 8 %
  (`"voice_speed"` 1.08, atempo, sin cambiar el tono). Elegido por Pol (opción C) el 20-11-2026.
- Cada toma varía (muestreo). `"voice_seed"` (por defecto 0) permite repetir con otras tomas.
- Escribe las cifras en letras en el guion ("diez mil euros", "tres por ciento").

`anterior/`: la voz oficial anterior (referencia WAV + texto, tono ~145 Hz), por si hay que volver a ella.
