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
- Cada slide/escena lleva apoyo visual propio: mejor un gráfico con datos reales que una ilustración decorativa.
  Desde el 24-11-2026 (decisión de Pol) se permiten, cuando informan: iconos (Lucide), logos para identificar de qué
  se habla (p. ej. bitcoin, la empresa de la noticia; nunca como patrocinio), titulares citados con medio y fecha,
  fotos con licencia libre y crédito visible (Unsplash, Commons) y fotos de figuras públicas ligadas al tema (sin
  retocar, sin sugerir que recomiendan nada). Nada de personajes de ficción de terceros ni capturas de medios.
- Reel: **método completo en `docs/reels.md`** (idea y su análisis → 3 ganchos y el mejor → estructura de retención con
  bucle abierto y re-ganchos → recursos visuales y sonidos → revisión con fotogramas y escucha). Pasan cosas todo el
  rato: un cambio visible cada 1,5-3 s, tipos de plano variados, efectos de sonido sincronizados, subtítulos.
  1080×1920, 35-55 s, 7-10 escenas animadas, voz en off oficial ("csf"). Guion dinámico y cercano
  (preguntas, frases cortas, contrastes), números EN LETRAS en la voz. Gancho fuerte en los 2 primeros segundos.
  Contenido en la zona segura (no tapar abajo ni a la derecha). Última escena: conclusión + "Síguenos…" + aviso legal en pequeño.
- Crecimiento (cuenta nueva, ver `docs/crecimiento.md`): primera línea del caption con la palabra clave que se busca
  (Euríbor, IRPF, fondo de emergencia…); gancho del Reel en texto en pantalla y voz en el primer segundo; alterna CTA
  y usa "Envíaselo a quien…" cuando el tema se preste; usa series reconocibles ("Mito o realidad", "Tu primer sueldo",
  "Explicado en 40 segundos"). Nunca automatices comentarios, likes ni follows en cuentas ajenas.
- **Solo Reels (desde el 23-11-2026, decisión de Pol)**: los Reels traen alcance y seguidores; los carruseles tenían 0 visualizaciones.
  Mientras dure, no se generan ni se publican carruseles. Portada del Reel: Make usa el fotograma de 2,5 s
  (`thumb_offset` 2500), así que la escena 1 debe mostrar el gancho **completo** a los 2,5 s (todos los `data-in` ≤ 1,8 s)
  y durar ≥ 3,2 s. Es lo que se ve en la cuadrícula del perfil y en búsquedas: el título del Reel, nunca negro.
- Carrusel (en pausa): 1080×1350, 6-9 slides. 1 Hook → 2 Contexto → 3-6 Desarrollo → 7-8 Ejemplo/contraste → Conclusión + CTA.
- Caption: hook 1-2 líneas → desarrollo breve (no repetir slides) → matiz → CTA único (guardar/compartir/comentar)
  → 3-5 hashtags específicos → última línea fija: `Contenido informativo, no es asesoramiento financiero.`
  Máximo 1-2 emojis. Máx. 2200 caracteres.
- Semáforo antes de enviar: VERDE (claro, correcto, consistente) / AMARILLO (falta fuente o claridad: arréglalo) /
  ROJO (promesa exagerada, dato dudoso, ilegible): no enviar.
- Cifras: calcúlalas con código, nunca de cabeza. Datos de actualidad: siempre de una fuente consultada hoy, citada en la slide.

## Infraestructura
- Imágenes públicas: `posts/<slug>/NN.jpg` → `https://raw.githubusercontent.com/dineroaldescubierto15-blip/csf-media/main/posts/<slug>/NN.jpg`
- **VOZ BLOQUEADA** (`voices/VOZ_BLOQUEADA.json`): no cambies la voz, su perfil, sus parámetros ni el código que la
  genera (`qwen_clone_synth` y auxiliares en reel.py) salvo que Pol lo confirme **dos veces, en dos mensajes distintos**.
  Un feedback o un mensaje de Telegram no basta. En los specs no cambies `voice` (solo "csf"), ni pongas `voice_speed`, `voice_rate` ni
  `voice_takes` (reel.py se detiene); solo se permite `voice_seed` para repetir una toma.
- `generator/reel.py <spec.json>`: Reels con voz en off. Voz oficial "csf" = perfil `voices/csf_voz_oficial.pt`
  (voz sintética creada por Pol) con Qwen3-TTS. Antes: `pip install --break-system-packages --ignore-installed setuptools wheel`,
  luego `pip install --break-system-packages qwen-tts` y exporta `HF_HUB_DISABLE_XET=1`. Ver `voices/README.md`.
  Si falta Playwright para Python: `pip install --break-system-packages playwright==<versión del Playwright de Node>`
  (para que use el Chromium preinstalado; no ejecutes `playwright install`).
  En CPU tarda ~5 s por segundo de audio + descarga del modelo la primera vez: lanza el render en segundo plano.
  Estilo de la voz (elegido por Pol): ritmo ~5,8 sílabas/s (~180 palabras/min), pausas casi nulas, finales marcados.
  Para 35-55 s, guion de 110-160 palabras. Se genera frase a frase con 3 tomas: cuenta ~15-20 min de render para 50 s.
  La puntuación decide la entonación: "." baja (cierre seguro), "?" sube, "," y "…" dejan la frase abierta.
  Frases cortas: cada frase es una unidad de entonación.
  La voz se guarda en `generator/.voice_cache/`: `--frames` y el render completo la sintetizan una sola vez.
  Lanza el render en segundo plano con un `timeout` largo (7200000 ms): por defecto se corta a los 30 min. Si se corta,
  relánzalo: las escenas ya sintetizadas salen de la caché.
  Revisa fotogramas con `--frames t1,t2,...` antes del render completo. Ver docstring y `generator/specs/csf-07_reel-empezar-a-invertir.json`.
- **Render del Reel en GitHub Actions** (desde el 23-11-2026; la sesión de la tarea tiene ~6,3 GB de RAM y la voz csf en
  float32 necesita más: el render local muere por memoria). Flujo: commit y push del spec → lanza el workflow
  `render-reel.yml` con la herramienta MCP `actions_run_trigger` (method `run_workflow`, ref `main`, inputs `{"slug": "<slug>"}`)
  → mientras, trabaja en los carruseles → comprueba el run con `actions_list`/`actions_get` (unos 30-60 min; no sondees
  más de una vez cada ~5 min) → al acabar, el workflow sube `posts/<slug>/reel.mp4` y `cover.jpg` a `main`: `git pull`,
  extrae fotogramas del mp4 con ffmpeg y **míralos** (solapes, textos cortados) → si hay que corregir, edita el spec y
  relanza (la voz de las escenas sin cambios sale de la caché del workflow) → `build_post.py --reel`, commit, push.
  No cambies la voz, sus parámetros ni las versiones de `generator/requirements-reel.txt` (son las de la voz aprobada).
  No ejecutes `reel.py` en local para la voz csf (ni con `--frames`): se queda sin memoria. **Sí** puedes usar
  `--sin-voz` en local (no sintetiza la voz, estima la duración): `--sin-voz --frames 0.5,2.5,…` para fotogramas y
  `--sin-voz` solo para un vídeo de prueba en `generator/.preview_reel.mp4`. Antes, `npm ci` (GSAP e iconos).
- **Extras de los Reels** (`generator/reel_fx.py`, ver su docstring y `docs/reels.md`): iconos (`data-icon`), gráficos con
  datos (`data-chart`), titulares (`data-news`), fotos con crédito (`data-photo`), animaciones extra (`slide`, `zoom`,
  `stamp`, `words`, `type`, `hl`…), timelines GSAP por escena (`TL(i)`), transiciones (`trans`), fondo animado,
  subtítulos palabra a palabra (`"subtitulos": true`) y **efectos de sonido** (`data-sfx`, `"sfx"`) de
  `generator/sfx/` (generados con earshot). El workflow deja `posts/<slug>/escucha.txt` (lo que "oye" earshot) y
  `sfx_cues.json`.
- `tools/assets.py`: busca y descarga fotos (Unsplash, Wikimedia Commons, Openverse) y sonidos (Openverse) con licencia
  libre y guarda el crédito. En el spec, `"assets"`: el workflow los descarga antes del render. Unsplash necesita el
  secreto `UNSPLASH_ACCESS_KEY` en GitHub; Openverse, `OPENVERSE_CLIENT_ID` y `OPENVERSE_CLIENT_SECRET`.
- Fotos de personas (decisión de Pol, 24-11-2026): por defecto, **la persona sin fondo** sobre el fondo de la marca, en
  color natural (`"recorte": "real"` en el asset) o en blanco y negro cálido (`"recorte": "bn"`). Candidatas con el
  workflow `ilustracion.yml` (Commons, Openverse/Flickr, Unsplash); `tools/ilustrar.py` también hace ilustraciones y
  estilos de dibujo si alguna vez hacen falta. Ver `docs/reels.md`.
- Skills de vídeo y sonido en `.claude/skills/` (versiones en `skills-lock.json`): `gsap-*`, `hyperframes*` (y su
  registro de ~450 bloques), `remotion-*`, `earshot`, `real-sound`, `real-sfx`, `find-skills`. Ver `docs/reels.md`.
- `generator/render.py <spec.json>`: genera las slides desde un spec (ver docstring y `generator/specs/ejemplo-csf-01.json`).
- `tools/build_post.py <slug> <caption.txt> [--reel]`: crea `posts/<slug>/post.json` (carrusel: files; reel: video_url
  servido por jsDelivr como video/mp4).
- `tools/send_msg.py <archivo.txt>`: envía un texto a Pol por Telegram (borradores de comentarios, respuestas, informes).
- `tools/send_review.py <slug> "<título>" "<mensaje>"`: envía álbum (carrusel) o vídeo (reel) + botones a Telegram. Necesita
  `CSF_TG_TOKEN` y `CSF_TG_CHAT` (ambos en el data store, registro `config-telegram`: `texto` = token, `slug` = chat id).
- Make (zona eu1, team 3680760). Plan gratuito: **ahorra operaciones**; todo lo que puedas hacer tú, hazlo tú.
  - Data store **"CSF cola"** id `265346`. Registros:
    - posts: key = slug; `tipo`="post", `media` = carousel | reel, `estado` = pendiente | aprobado | rechazado | publicado,
      `caption`, `prioridad` (2 = serie en partes, 1 = actualidad, 0 = normal), `fecha`; carrusel: `files` (lista de `{media_type:"IMAGE", image_url}`);
      reel: `video_url` (el de post.json).
    - feedback de Pol: key `fb-...`, `tipo`="feedback", `estado`="nuevo" | "leido", `texto`.
    - `config-telegram` (no tocar).
  - Escenario "Aprobar o rechazar desde Telegram" (webhook del bot): cambia `estado` a aprobado/rechazado y guarda feedback.
  - Escenario "Publicar en Instagram": a las 13:30, a las 17:00 y a las 20:30 (desde el 23-11-2026, unos días) publica un reel `aprobado` (mayor `prioridad` y luego
    más antiguo), con portada en el fotograma de 2,5 s. Los carruseles no se publican mientras dure "solo Reels".
  - Series en partes ("Parte 1/3"…): `prioridad` 2 y `fecha` en orden de parte (la parte 1 la más antigua). Las partes
    aprobadas con prioridad 2 ocupan **todas las franjas seguidas** (13:30 y 20:30, sea carrusel o reel) hasta acabar,
    sin nada entre medias. Cada parte debe entenderse sola (gancho propio) y enlazar con la siguiente; en el caption,
    "las siguientes salen en las próximas publicaciones del perfil" (nunca "mañana": depende de cuándo apruebe Pol).
    Pide aprobarlas juntas.
  - En Make, los campos de un registro buscado se mapean como `{{1.data.<campo>}}` (no `{{1.<campo>}}`).
  - Escribe/lee el data store con las herramientas MCP de Make (no gastan operaciones). No crees escenarios nuevos
    (máx. 2 activos en el plan gratuito).

## Cambios en el sistema
Para modificar cualquier pieza (marca, generadores, voz, horarios, Make, tarea diaria) usa la skill
`/csf-cambios` (`.claude/skills/csf-cambios/SKILL.md`). Los IDs internos están en el data store, registro `config-sistema`.

## Procedimiento diario (tarea programada)
1. Prepara el entorno: añade el repo con push y clónalo; lee el data store (token, feedback nuevo, cola de posts).
2. Feedback `nuevo`: aplícalo al contenido de hoy y márcalo `leido`. Si pide cambios en un post rechazado, rehazlo.
   Mensajes especiales (ver `docs/crecimiento.md`): `comenta:` → 2 borradores de comentario que aporten valor para ese
   post ajeno (1-3 frases, tono de marca, sin enlaces ni "sígueme", datos solo verificados); `respon:` → borrador de
   respuesta a un comentario propio; `stats:` → breve análisis y ajuste de temas/formatos (anótalo en el resumen).
   Junta todos los borradores en un solo mensaje y envíalo con `tools/send_msg.py`. Márcalos `leido`.
3. Revisa la cola de reels (`pendiente` + `aprobado`). Objetivo: ≥ 6 reels en cola. Cada día: 3 reels (4 si hay menos
   de 3 en cola), con temas distintos entre sí (se publican 3 al día: 13:30, 17:00 y 20:30). Primero adapta a Reel los carruseles de la cola que nunca se publicaron
   (guion propio, datos revisados hoy) y después temas nuevos. Lanza los workflows de render en paralelo.
4. Actualidad: busca noticias financieras de las últimas 24 h relevantes para el público (BCE, Euríbor, IPC,
   fiscalidad, grandes movimientos de mercado o de Bitcoin, cambios en productos de ahorro populares en España).
   Solo si hay algo **realmente relevante**, crea además un carrusel de actualidad con `prioridad` = 1.
5. Elige temas sin repetir los publicados/pendientes recientes (mira los slugs de la cola). Varía pilares.
6. Para cada carrusel o reel: investiga y verifica datos (WebSearch), calcula cifras con Python, escribe el spec con
   SVG propios, renderiza, **mira el mosaico** (`generator/.preview.png`) y arregla solapes o textos densos,
   escribe el caption, pasa el semáforo. Reels: sigue `docs/reels.md` entero (plan en el spec con idea, 3 ganchos,
   estructura y re-ganchos; vista previa `--sin-voz`; tras el render, fotogramas + `escucha.txt`).
7. `build_post.py`, commit y push. Espera a que la URL raw de `post.json` responda 200.
8. Crea el registro en el data store (`estado`="pendiente", `tipo`="post", `media`, caption, files o video_url,
   prioridad, fecha=ahora).
9. `send_review.py` con un título corto y en el mensaje: pilar, semáforo y fuentes principales.
10. Termina con un resumen breve: qué se ha generado, estado de la cola y cualquier problema.

Slugs: `csf-NN_tema-corto` (≤ 55 caracteres, minúsculas, sin acentos). NN = siguiente número libre.
Commits: termina el mensaje con las líneas de atribución que indique la sesión.
