# Capital Sin Filtros — guía operativa para Claude

Cuenta: **@capital.sin.filtros** (Instagram, IG user id 17841428832055293). Dueño: Pol.
Este repositorio es **público**: nunca escribas aquí tokens, IDs privados ni datos personales.

El manual de marca completo está en Google Drive (carpeta "Claude/01_Marca", archivo
`Manual_de_Marca_Capital_Sin_Filtros_v1.1.docx`, id `1K1Dj4Z_9j_mqNWrVkl_v9AN-TsGVjaL2`).
Lo esencial está resumido abajo; si dudas, léelo.

## Marca en 20 líneas
- Promesa: "Finanzas explicadas de forma clara, directa y sin humo". Educación, no riqueza rápida.
- Público: 18-30 años, España, español de España, tratamiento de **tú**. La marca no habla en primera persona.
- Tono: directo, racional, sobrio, cercano, crítico con mitos, práctico. Amigo informado, nunca gurú.
- Prohibido: FOMO, urgencia inventada, "secretos", "los bancos no quieren que sepas", prometer rentabilidades,
  ocultar riesgos, opiniones como hechos, afirmaciones absolutas, recomendaciones personalizadas.
- Pilares (alternarlos, no repetir concepto+ángulo seguidos): Ahorro y hábitos · Inversión · Vivienda ·
  Deuda y crédito · Mercados · Finanzas personales · Mitos y errores · Actualidad explicada · Cripto (solo explicativo).
- Cripto: explicar, noticias, análisis de BTC/ETH, memecoins como fenómeno. **Nunca** recomendar comprar.
- Productos reales (p. ej. cuentas remuneradas): permitido con condiciones completas (TAE, requisitos, límites,
  duración, FGD 100.000 €, fecha de los datos). Nunca "el mejor" en absoluto. Patrocinado → "Publicidad" visible en la slide.
- Visual: fondo #0A0A0A, texto #F5F5F2, dorado #F4C542 solo para la cifra/palabra clave; slides de contraste en #E7E7E3.
  Inter. Mucho espacio. 1 slide = 1 idea. Fuente en pequeño bajo cada dato. Sin emojis en slides.
- Cada slide lleva apoyo visual propio: mejor un gráfico con datos reales que una ilustración decorativa.
  Ilustraciones planas, solo paleta de marca, sin fotos ni personas reales, sin marcas/personajes de terceros.
- Carrusel: 1080×1350, 6-9 slides. 1 Hook → 2 Contexto → 3-6 Desarrollo → 7-8 Ejemplo/contraste → Conclusión + CTA.
- Caption: hook 1-2 líneas → desarrollo breve (no repetir slides) → matiz → CTA único (guardar/compartir/comentar)
  → 3-5 hashtags específicos → última línea fija: `Contenido informativo, no es asesoramiento financiero.`
  Máximo 1-2 emojis. Máx. 2200 caracteres.
- Semáforo antes de enviar: VERDE (claro, correcto, consistente) / AMARILLO (falta fuente o claridad: arréglalo) /
  ROJO (promesa exagerada, dato dudoso, ilegible): no enviar.
- Cifras: calcúlalas con código, nunca de cabeza. Datos de actualidad: siempre de una fuente consultada hoy, citada en la slide.

## Infraestructura
- Imágenes públicas: `posts/<slug>/NN.jpg` → `https://raw.githubusercontent.com/dineroaldescubierto15-blip/csf-media/main/posts/<slug>/NN.jpg`
- `generator/reel.py <spec.json>`: Reels con voz en off (Kokoro; antes `pip install --break-system-packages kokoro-onnx piper-tts`). Ver docstring y `generator/specs/reel-ejemplo.json`.
- `generator/render.py <spec.json>`: genera las slides desde un spec (ver docstring y `generator/specs/ejemplo-csf-01.json`).
- `tools/build_post.py <slug> <caption.txt>`: crea `posts/<slug>/post.json` (caption + files + telegram_media).
- `tools/send_review.py <slug> "<título>" "<mensaje>"`: envía álbum + botones a Telegram. Necesita
  `CSF_TG_TOKEN` y `CSF_TG_CHAT` (ambos en el data store, registro `config-telegram`: `texto` = token, `slug` = chat id).
- Make (zona eu1, team 3680760). Plan gratuito: **ahorra operaciones**; todo lo que puedas hacer tú, hazlo tú.
  - Data store **"CSF cola"** id `265346`. Registros:
    - posts: key = slug; `tipo`="post", `estado` = pendiente | aprobado | rechazado | publicado, `caption`, `files`
      (lista de `{media_type:"IMAGE", image_url}`), `prioridad` (1 = actualidad, 0 = normal), `fecha`.
    - feedback de Pol: key `fb-...`, `tipo`="feedback", `estado`="nuevo" | "leido", `texto`.
    - `config-telegram` (no tocar).
  - Escenario "Aprobar o rechazar desde Telegram" (webhook del bot): cambia `estado` a aprobado/rechazado y guarda feedback.
  - Escenario "Publicar en Instagram (13:30)": cada día publica el post `aprobado` con mayor `prioridad` y luego más antiguo.
  - Escribe/lee el data store con las herramientas MCP de Make (no gastan operaciones). No crees escenarios nuevos
    (máx. 2 activos en el plan gratuito).

## Procedimiento diario (tarea programada)
1. Prepara el entorno: añade el repo con push y clónalo; lee el data store (token, feedback nuevo, cola de posts).
2. Feedback `nuevo`: aplícalo al contenido de hoy y márcalo `leido`. Si pide cambios en un post rechazado, rehazlo.
3. Revisa la cola: cuenta posts `pendiente` + `aprobado`. Objetivo: siempre ≥ 3 en cola.
   Genera 1 carrusel normal cada día; 2 si la cola tiene menos de 3.
4. Actualidad: busca noticias financieras de las últimas 24 h relevantes para el público (BCE, Euríbor, IPC,
   fiscalidad, grandes movimientos de mercado o de Bitcoin, cambios en productos de ahorro populares en España).
   Solo si hay algo **realmente relevante**, crea además un carrusel de actualidad con `prioridad` = 1.
5. Elige temas sin repetir los publicados/pendientes recientes (mira los slugs de la cola). Varía pilares.
6. Para cada carrusel: investiga y verifica datos (WebSearch), calcula cifras con Python, escribe el spec con
   SVG propios, renderiza, **mira el mosaico** (`generator/.preview.png`) y arregla solapes o textos densos,
   escribe el caption, pasa el semáforo.
7. `build_post.py`, commit y push. Espera a que la URL raw de `post.json` responda 200.
8. Crea el registro en el data store (`estado`="pendiente", `tipo`="post", caption, files, prioridad, fecha=ahora).
9. `send_review.py` con un título corto y en el mensaje: pilar, semáforo y fuentes principales.
10. Termina con un resumen breve: qué se ha generado, estado de la cola y cualquier problema.

Slugs: `csf-NN_tema-corto` (≤ 55 caracteres, minúsculas, sin acentos). NN = siguiente número libre.
Commits: termina el mensaje con las líneas de atribución que indique la sesión.
