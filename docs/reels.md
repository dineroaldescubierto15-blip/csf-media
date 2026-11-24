# Cómo se hace un Reel de Capital Sin Filtros (método desde el 24-11-2026)

Objetivo de Pol: Reels **profesionales, elaborados y fáciles de seguir**, en los que **pasan cosas todo el rato** para
mantener la atención. No basta con "se ve bien": cada segundo tiene que dar un motivo para quedarse.

El proceso tiene 6 fases. Las fases 1-3 se escriben en el spec, en el campo `"plan"` (reel.py lo ignora; sirve para
pensar, revisar y que Pol entienda la intención). No se renderiza nada sin plan.

---

## 1. Idea (y su análisis)

1. Fuente de la idea: una búsqueda real del público (18-30, España), una noticia de las últimas 24-48 h, un mito
   que se repite o un error caro y común. Anota la **palabra clave** que alguien buscaría (Euríbor, IRPF, bitcoin…).
2. Escribe la **promesa** en una frase: qué sabrá o podrá hacer quien vea el Reel hasta el final.
3. Pasa el **test de la idea** (si falla uno, cambia el ángulo o la idea):
   - ¿Se entiende en una frase de 12 palabras?
   - ¿Hay tensión? (dinero en juego, sorpresa, contradicción, un error que comete mucha gente, una noticia que afecta).
   - ¿Hay al menos **un dato real y verificable** que sorprenda? (fuente consultada hoy).
   - ¿El final responde de verdad la promesa? (sin clickbait: lo que promete el gancho se cumple).
   - ¿Cumple la marca? (sin promesas de rentabilidad, sin recomendar comprar, sin FOMO).
4. Elige el **ángulo**: "lo que nadie te cuenta de…", "mito o realidad", "qué significa para ti", "cuánto cuesta de
   verdad", "el error que…", "explicado en 40 segundos", serie en partes.

## 2. Gancho (0-2 s): la parte más importante

Escribe **3 ganchos distintos**, puntúalos de 1 a 5 en claridad, curiosidad, relevancia para 18-30 y concreción, y
quédate con el mejor (anótalo en el plan). Fórmulas que funcionan:

| Fórmula | Ejemplo |
|---|---|
| Cifra que choca + pregunta | "¿Bitcoin a la mitad de precio en un año?" |
| Contradicción | "Que te suban el sueldo puede hacer que cobres menos… ¿o no?" |
| Error con coste | "Este error con la tarjeta te puede costar 600 € al año." |
| Noticia + "qué significa para ti" | "El BCE ha subido los tipos. Tu hipoteca ya lo nota." |
| Reto | "Adivina cuánto necesitas ahorrar para comprar un piso de 200.000 €." |
| Lo prohibido de la marca | ~~"El secreto que los bancos no quieren que sepas"~~ (nunca) |

Reglas del gancho:
- La **voz y el texto en pantalla dicen lo mismo** en el primer segundo (mucha gente ve sin sonido).
- Desde el **fotograma 0** hay algo grande moviéndose (icono, cifra, foto con zoom): nada de empezar en negro.
- Es la **portada**: Make usa el fotograma de 2,5 s, así que a los 2,5 s el gancho está **completo** (todos los
  `data-in` de la escena 1 ≤ 1,8 s) y la escena dura ≥ 3,2 s.
- Una sola idea, máximo 8 palabras grandes. Un efecto de sonido fuerte (`impact` o `whoosh`) en el primer segundo.

## 3. Estructura de retención (35-55 s, 7-10 escenas)

| Tramo | Qué pasa | Herramientas típicas |
|---|---|---|
| 0-2 s | **Gancho** | icono/cifra con `stamp`/`spin`, `impact` |
| 2-6 s | **Contexto + bucle abierto**: por qué importa y qué vas a descubrir ("y lo tercero es lo que casi nadie mira") | titular `data-news`, foto, `paper` |
| 6-35 s | **Desarrollo en 3-4 golpes**: cada golpe = mini-pregunta → respuesta visual. Escala: de lo conocido a lo sorprendente | gráfico real `data-chart`, comparación lado a lado, lista que se completa, contador `count` |
| cada 8-10 s | **Re-gancho**: "pero ojo", "aquí viene lo raro", una pregunta, un giro | `glitch`, `shake`, `riser` |
| 35-45 s | **Recompensa**: se cierra el bucle con el dato o la conclusión más fuerte | cifra grande, `impact`, `success` |
| últimos 4-6 s | Conclusión + "Síguenos…" + aviso legal en pequeño (y "Envíaselo a quien…" si encaja) | `chip`, icono, `ding` |

Ritmo visual (lo que hace que "pasen cosas"):
- **Un cambio visible cada 1,5-3 s**: un elemento nuevo, un zoom, un icono, una línea que se dibuja, un subrayado,
  una transición. Nada quieto más de 3 s.
- **Una idea por escena**, escenas de 3-7 s. Máximo 7-8 palabras grandes por pantalla; el resto, en la voz.
- **Varía el tipo de plano**: texto grande → icono + cifra → gráfico → titular → foto → comparación → lista. No
  repitas el mismo tipo dos escenas seguidas.
- **Transiciones** variadas (`"trans": "slide" | "zoom" | "whip" | "cut"`), con `cut` en los golpes secos.
- **Subtítulos** palabra a palabra (`"subtitulos": true`) por defecto: la mayoría ve sin sonido. Si una escena ya
  muestra exactamente la frase de la voz, no pasa nada: los subtítulos van abajo y en pequeño.
- **Sonido**: whoosh suave automático en cada transición; `pop` en iconos, `paper` en titulares, `camera` en fotos,
  `tick` en contadores, `cash`/`coin` con dinero, `riser` antes de la recompensa, `impact` en la cifra clave (1-2 por
  Reel), `glitch`/`error` al desmontar un mito, `success` en "realidad". Máximo ~1 efecto cada 1,5 s y nunca encima
  de la palabra clave de la voz.

Guion (voz): frases cortas, preguntas, contrastes; números EN LETRAS; 110-160 palabras. La puntuación decide la
entonación (ver CLAUDE.md). La voz está **bloqueada**: no se tocan sus parámetros.

## 4. Recursos visuales (de dónde sale cada cosa)

| Necesito… | Cómo | Notas |
|---|---|---|
| Icono | `<i data-icon="lucide:piggy-bank" data-size="160" class="g" data-in=".3" data-a="pop" data-sfx="pop"></i>` | 1.500 iconos Lucide (ISC). Marcas: `si:bitcoin`, `si:ethereum`, `si:nvidia`… (Simple Icons, CC0) |
| Gráfico con datos reales | `<div data-chart='{"type":"line","data":[…],"labels":[…],"unit":" €","in":.3,"d":1.6,"sfx":"riser"}'></div>` | Datos calculados con Python, fuente y fecha en un `.src` debajo. `bar` para comparar (con `mark`) |
| Titular de noticia | `<div data-news='{"medio":"Expansión","fecha":"24/11/2026","titular":"El BCE **sube** los tipos"}'></div>` | Titular literal (cita breve), medio y fecha reales; sin logos ni capturas. Fuente también en el caption |
| Foto de una persona | `python3 tools/assets.py buscar commons "Christine Lagarde"` → elegir → en el spec `"assets"` → `data-photo` con su `"credito"` | Solo figuras públicas relacionadas con el tema, foto con licencia libre (Commons), sin retocar, sin sugerir que recomiendan nada |
| La foto de la persona no queda bien (borrosa, de perfil, fondo feo) | Workflow `ilustracion.yml` (`id`, `persona`): busca candidatas en Commons → elige la mejor → otra vez con `foto` = `cand_NN.jpg` → `posts/_ilustraciones/<id>/ilus/ilus_pintura.jpg` (también `editorial` y `duotono`; estilos de dibujo con `tools/ilustrar.py dibujo`: cómic, póster, lápiz, trama, línea, acuarela). En local: `tools/ilustrar.py` | Ilustración realista hecha SOBRE la foto real (misma cara, sin cambiar expresión ni añadir nada). Crédito: "Ilustración: Capital Sin Filtros, a partir de una foto de …" |
| Foto genérica (bolsa, casa, supermercado) | `"assets": [{"id":"bolsa","de":"unsplash","q":"stock market screen","orient":"portrait"}]` | Crédito "Foto: X / Unsplash" visible |
| Sonido real concreto (campana de bolsa, caja registradora…) | `"assets": [{"id":"campana","de":"openverse-audio","q":"bell ring"}]` y `"sfx": [{"t":1.2,"s":"../../posts/<slug>/assets/campana"}]` | CC0/CC BY/BY-SA; crédito en el caption si es CC BY |
| Efecto que no está en `generator/sfx/` | `earshot make "<descripción>" -o generator/sfx/<nombre>.wav` y añádelo a `CREDITS.md` | Sin red ni licencias: lo genera earshot |
| Animación a medida | GSAP dentro de la escena: `<script>const tl = TL(3); tl.from("#a", {...}, .2)</script>` | Skills `gsap-*`. Deterministas: sin timers ni `Math.random()` |
| Un efecto con nombre (glitch, kinetic type, marcador…) | Busca antes en `/hyperframes-registry` y adapta el bloque (HTML + GSAP) a una escena con `TL(i)` | Mismo contrato que HyperFrames: timeline en pausa que se busca por tiempo |
| Pieza especial (mapa animado, 3D) | Remotion (skills `remotion-*`) o HyperFrames, renderizado aparte y como vídeo de fondo | Remotion: gratis para particulares y empresas pequeñas |

Las fotos y sonidos del spec (`"assets"`) se descargan solos en GitHub Actions antes del render
(`tools/assets.py resolver`), con sus créditos en `posts/<slug>/assets/creditos.json`. Si la sesión tiene acceso a
esos dominios, puedes buscarlos y bajarlos antes para mirarlos (`tools/assets.py hoja <slug>`).

## 5. Montaje en el spec

```json
{ "slug": "csf-NN_tema", "music_seed": 3, "subtitulos": true, "fondo": "grid",
  "plan": {"idea": "...", "promesa": "...", "palabra_clave": "...", "ganchos": ["...", "...", "..."], "gancho": "...",
           "bucle": "...", "golpes": ["...", "...", "..."], "re_ganchos": ["8 s: ...", "18 s: ..."], "recompensa": "...",
           "cta": "..."},
  "assets": [{"id": "persona", "de": "commons", "q": "..."}],
  "scenes": [ {"voz": "...", "trans": "cut", "html": "...", "sfx": [{"t": 0.1, "s": "impact"}]}, ... ] }
```
Referencia completa de componentes, animaciones y sonidos: docstring de `generator/reel_fx.py`.
Zona segura: contenido entre y = 260 y 1480, x = 90-930 (con subtítulos, el contenido queda por encima de y ≈ 1280).

## 6. Revisión (antes de enviar a Pol)

1. **Vista previa gratis, sin voz**: `python3 generator/reel.py <spec> --sin-voz --frames 0.5,2.5,5,...` (no
   sintetiza la voz, estima la duración) y mira los fotogramas: solapes, textos cortados, zona segura, legibilidad.
   `--sin-voz` sin `--frames` hace un vídeo completo en `generator/.preview_reel.mp4` para revisar ritmo y sonidos.
2. Render real en GitHub Actions (CLAUDE.md). Al acabar: extrae fotogramas del mp4 y míralos.
3. **Escucha** (no puedes oír): lee `posts/<slug>/escucha.txt` (informe de earshot: secciones, eventos, volumen,
   sincronía con los cortes) y `posts/<slug>/sfx_cues.json`. Busca efectos que tapen la voz (> +12 dB sobre el fondo
   justo en una palabra clave), silencios largos o un volumen integrado fuera de -16 a -12 LUFS. Para escuchar algo
   concreto: `earshot describe|match|critique <archivo>` (skill `earshot`).
4. **Checklist de retención**: ¿el gancho está completo a los 2,5 s? ¿hay un cambio visible cada ≤ 3 s? ¿hay al menos
   3 tipos de plano distintos? ¿se cierra el bucle abierto? ¿cada dato tiene fuente y fecha en pantalla?
5. Semáforo de marca (CLAUDE.md) y envío a Pol.

## Herramientas instaladas (skills en `.claude/skills/`, versiones en `skills-lock.json`)

- `gsap-*` (GreenSock, MIT): animación. `hyperframes*`, `media-use`, `style-sampling` ("Finance Explainer"),
  `reverse-any-video`… (HeyGen, Apache 2.0): HTML → vídeo y ~450 bloques reutilizables.
- `remotion-*` (Remotion): vídeo en React. Licencia gratuita para particulares y empresas pequeñas.
- `earshot` y `real-sound` (MIT): generar efectos y **escuchar** audio. `real-sfx` (Clipwing, scripts MIT): diseño de
  sonido sobre un vídeo terminado con sonidos reales.
- `find-skills` (Vercel): cuando haga falta una capacidad nueva, `npx skills find <tema>`. Instala solo de fuentes
  conocidas, revisa el SKILL.md antes, añade con `npx skills add <repo> -a claude-code -y` y cuéntaselo a Pol.
- Fotos y sonidos: `tools/assets.py` (Unsplash con `UNSPLASH_ACCESS_KEY`, Wikimedia Commons, Openverse).
