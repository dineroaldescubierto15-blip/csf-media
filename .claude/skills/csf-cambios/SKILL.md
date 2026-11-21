---
name: csf-cambios
description: Hacer cambios en el sistema de contenido de @capital.sin.filtros (marca, carruseles, Reels, voz, horarios, Make, tarea diaria). Úsalo cuando Pol pida modificar cómo se genera, revisa o publica el contenido.
---

# Cambios en el sistema de Capital Sin Filtros

Pol pide un cambio con sus palabras (en catalán o castellano). Tu trabajo: entenderlo, aplicarlo donde toca,
probarlo y explicarle el resultado en catalán, breve y sin tecnicismos.

## 0. Antes de tocar nada
- Lee `CLAUDE.md` entero: describe la marca, las piezas y el procedimiento diario.
- Lee del data store de Make "CSF cola" (id 265346, herramientas MCP de Make) el registro `config-sistema`:
  su campo `texto` es un JSON con los IDs (escenarios, conexiones, cuenta de Instagram, tarea diaria, carpetas de Drive).
  El registro `config-telegram` tiene el token del bot (`texto`) y el chat de Pol (`slug`). Nunca escribas estos datos
  en el repositorio (es público) ni los repitas a Pol.
- Si el cambio es ambiguo y equivocarse sería caro, pregunta una sola cosa concreta. Si no, decide y sigue.

## 1. Dónde va cada tipo de cambio
| Pol pide… | Dónde se cambia |
|---|---|
| Temas, tono, más/menos de un pilar, captions | `CLAUDE.md` (sección de marca/procedimiento). Si es puntual para mañana, basta un registro de feedback en el data store (`tipo`="feedback", `estado`="nuevo"). |
| Aspecto de los carruseles | `generator/render.py` (CSS/tipos de slide) y, si aplica, el ejemplo en `generator/specs/` |
| Aspecto, ritmo o duración de los Reels, subtítulos | `generator/reel.py` y la guía de Reels en `CLAUDE.md` |
| Voz (tono, velocidad, otra voz) — **BLOQUEADA**: solo con confirmación explícita de Pol dos veces (dos mensajes); luego actualiza `voices/VOZ_BLOQUEADA.json` | `voices/` (referencia oficial + README) y el motor en `generator/reel.py`. Tras cambiarla, mide el tono (F0) y genera una muestra |
| Horarios de publicación, qué se publica | Escenario de publicación en Make (`escenario_publicar`). Pide primero el blueprint con `scenarios_get`, edítalo y envíalo entero |
| Aprobación por Telegram | Escenario `escenario_aprobar` (mismo método) y/o `tools/send_review.py` |
| Cuántas piezas al día, qué hace la tarea de cada mañana | Prompt de la tarea programada (`tarea_diaria_id`) con `update_trigger`, y el procedimiento de `CLAUDE.md` |
| Manual de marca | `CLAUDE.md` y, si Pol lo quiere, el .docx de Drive (`drive_marca`) |

## 2. Reglas
- Make está en el plan gratuito: máximo 2 escenarios activos y ~1.000 operaciones/mes. No crees escenarios nuevos;
  amplía los existentes. Todo lo que puedas hacer tú (renderizar, enviar a Telegram, escribir en el data store vía MCP), hazlo tú.
- Nunca publiques en Instagram por tu cuenta ni cambies la cuenta de destino. Si una prueba requiere publicar, pide permiso.
- Mantén las reglas de marca (sin promesas de rentabilidad, sin recomendar comprar cripto, aviso legal en el caption).
- No clones voces de personas reales.
- Cambios en código: commit y push a `main` con un mensaje claro (termina con las líneas de atribución que indique la sesión).

## 3. Probar antes de dar por hecho
- Visual de carrusel: renderiza un spec de ejemplo y mira `generator/.preview.png`.
- Reel: `--frames` para fotogramas clave; si cambia la voz o el ritmo, render completo.
- Telegram/Make: envía una prueba marcada como PRUEBA (registro con `tipo`="prueba" para que nunca se publique)
  y pide a Pol que pulse "Rechazar".
- Enseña a Pol el resultado (imagen, vídeo o mensaje de prueba) cuando el cambio sea visible.

## 4. Cierre
Resume a Pol en catalán: qué has cambiado, cómo lo has probado, desde cuándo se nota (p. ej. "a partir de la tarea de mañana")
y si queda algo pendiente por su parte.
