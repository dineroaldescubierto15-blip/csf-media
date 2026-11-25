# Método viral para los Reels (desde el 25-11-2026)

Este documento **manda sobre `docs/reels.md`** cuando se contradigan. Nace de la revisión del 25-11-2026: con 12
seguidores, pocas interacciones y una retención media por debajo de 10 s en vídeos de 45-58 s, el formato
"explicación completa y bonita" no funciona para crecer. Hay que hacer vídeos **más cortos, que enganchen en el
fotograma 0, den la respuesta pronto y se envíen**.

## 1. Lo que premia Instagram (con fuentes)
- Lo que Adam Mosseri (jefe de Instagram) ha dicho en público: las señales clave de los Reels son el **tiempo de
  visualización**, los **"me gusta" por alcance** y los **envíos por alcance** (sends per reach). Para llegar a gente que
  no te sigue, los **envíos por DM** son lo que más pesa. No hay pesos oficiales: no te creas cifras exactas.
- Lo que dicen los datos disponibles (de calidad media, hay que comprobarlo con nuestras estadísticas):
  - Una voz que habla en los primeros 3 s retiene más que la música sola (+11,7 % de retención a 3 s, Emplifi).
  - El texto en pantalla ayuda algo (+5 %).
  - Los Reels cortos (menos de 15-30 s) se completan más y se repiten más.
  - Los de 45-60 s tienen algo más de interacción, pero solo si ya retienen.
- Conclusión práctica para una cuenta nueva:
  - Retención y envíos antes que interacción.
  - Vídeos cortos que se vean enteros (o dos veces) y que la gente quiera mandar a alguien.

## 2. Diagnóstico de nuestros Reels (csf-07 a csf-33)
| Problema | Por qué hace perder gente | Regla nueva |
|---|---|---|
| Duran 45-58 s | Con <10 s de media, el 80 % del vídeo no lo ve nadie | 20-35 s (máx. 40 s en series) |
| El fotograma 0 está medio vacío (el título entra palabra a palabra) | El primer fotograma decide si paras de hacer scroll | Gancho **completo y quieto** en el fotograma 0; el movimiento lo da el zoom (`"ritmo"`) |
| Ganchos en pregunta genérica ("¿Podrías…?", "¿Es el café…?") | Una pregunta se responde mentalmente con "no" y sigues | Afirmación con **cifra concreta** o consecuencia para ti |
| La respuesta llega al final | Quien no aguanta no se lleva nada y no lo comparte | Respuesta antes del **40 %** del vídeo; luego, el giro |
| Pantallas con mucho texto pequeño | En el móvil no se lee y se ve "presentación" | 1 cifra grande por escena; el resto, en los subtítulos grandes |
| Subtítulos pequeños abajo | Mucha gente ve sin sonido | `"subtitulos": "grande"` (3 palabras, 92 px, centro-abajo) |
| Final largo: conclusión + "Síguenos" + aviso | Los últimos 4-5 s se van, y "síguenos" no lo pide el algoritmo | Cierre de ≤ 3 s con CTA de **envío** ("Envíaselo a quien…") |
| Temas "de manual" (fondo de emergencia, TIN vs TAE) | Útiles, pero nadie los manda a un amigo | Temas que **tocan la vida real** del público y dan un dato para discutir |
| Mismo esqueleto visual en todos | El ojo se acostumbra | Alternar formatos (sección 5) |

La voz está bloqueada (no se toca): el ritmo se gana con guiones más cortos, frases de 6-10 palabras y menos escenas
lentas, no cambiando la voz.

## 3. Reglas duras de un Reel (checklist antes de renderizar)
1. **Duración 20-35 s**: guion de **60-100 palabras** (formato Rápido 60-85, Explicado ≤ 100). Series: ≤ 110 por parte.
2. **Fotograma 0 = portada viva**: la escena 1 no lleva `data-in` (todo visible desde el principio). Contiene la cifra
   o la frase gancho en grande (≥ 150 px) y nada más que distraiga. Mira el fotograma 0 **y** el de 2,5 s (portada de Make).
3. **Primera frase**:
   - ≤ 14 palabras, dicha en ~3 s.
   - Afirmación concreta: cifra, consecuencia o contraste.
   - Nunca empieces con "Hoy te explico", "¿Sabías que…?", "En este vídeo", "Hola" ni con el nombre de la cuenta.
4. **Promesa clara en 3 s**: tiene que entenderse qué se va a llevar quien mire ("la cuenta", "el dato", "el error").
5. **Respuesta antes del 40 %**, después el giro ("¿Y con el salario mínimo?", "Pero en Madrid…").
6. **Re-gancho cada 6-8 s**: pregunta corta, "Haz la cuenta", "Ojo", "Y aquí viene lo bueno".
7. **Cambio visual cada 1,5-2,5 s**: escenas cortas (2-5 s) y `"ritmo": true` (golpe de zoom en cada escena).
8. **1 idea por vídeo, 1 cifra por escena**: el número va enorme y el texto pequeño queda solo para la fuente.
9. **Cierre ≤ 3 s**:
   - Remate de una frase y CTA de **envío** ("Envíaselo a quien está buscando piso").
   - El aviso legal va en pequeño en esa misma escena.
   - "Síguenos" solo de vez en cuando (o en el caption).
10. **Bucle** cuando se pueda: que la última frase empalme con la primera, para que se vea dos veces.
11. **Spec**:
    - Activa `"subtitulos": "grande"` y `"ritmo": true`.
    - En el `plan`, añade `formato` y `por_que_se_comparte`.
12. **Datos**: igual que siempre (fuente consultada hoy, cifras calculadas con Python, fuente en pequeño en pantalla).

## 4. Banco de ganchos (adaptados a la marca: sin FOMO, sin "secretos", sin prometer)
Plantillas (rellena con datos reales):
- **Cifra choque**:
  - "Para [algo normal] necesitas cobrar [cifra]."
  - "[Cifra] es lo que [algo cotidiano] te cuesta al año."
- **Contraste**:
  - "Mismo sueldo, [X] € más al mes. La diferencia es [cosa]."
  - "[A] y [B] cobran igual. Uno acaba con [X] € más."
- **Tu caso**:
  - "Si cobras [sueldo], esto es lo que te queda de verdad."
  - "Con [edad/sueldo], así se reparte tu nómina."
- **Error común**:
  - "El error de [situación] que cuesta [cifra]."
  - "Casi nadie calcula esto antes de [decisión]."
- **Mito**: "'[Frase que se oye mucho].' Es mentira, y te lo enseño con números." (Mito o realidad)
- **Haz la cuenta**:
  - "[Cifra A] entre [B]: el resultado no te va a gustar."
  - "Haz esta cuenta antes de [decisión]."
- **Actualidad**:
  - "[Noticia] cambia esto en tu bolsillo: [cifra]."
  - "Ayer [hecho con fecha]. Esto es lo que significa para ti."
- **Comparación con fuera**: "En [país] cobran [X] por lo mismo. Pero ojo con [matiz]."
- **Tiempo de vida**: "Esto son [N] horas de tu trabajo."
- **Ranking**: "3 gastos que más pesan en tu sueldo (el primero no es el que crees)."

Prohibido (marca y retención):
- "Los bancos no quieren que sepas", "el secreto", "hazte rico", urgencia inventada.
- Preguntas de sí/no sin cifra.
- Empezar con contexto ("En 2008…") en lugar de con la consecuencia.

## 5. Formatos (alternarlos; cada uno con su esqueleto)
| Formato | Duración | Esqueleto |
|---|---|---|
| **Haz la cuenta** | 20-30 s | Cifra gancho → de dónde sale (2 datos) → la cuenta en pantalla → giro → envío |
| **Mito en 20 segundos** | 15-25 s | Frase del mito → "MITO" en sello → la prueba con un número → remate |
| **Lo que cuesta de verdad** | 25-35 s | Precio que ves → lo que pagas al final → el coste escondido → consejo neutro |
| **Sueldo real** | 25-35 s | "Si cobras X brutos…" → reparto de la nómina (gráfico) → lo que queda → comparación |
| **A vs B** | 20-30 s | Dos opciones → elige → resultado en euros → matiz |
| **Actualidad en 30 s** | 25-35 s | Titular con fecha → qué cambia para ti (cifra) → qué vigilar |
| **Serie en partes** | 30-40 s c/u | Cada parte con su gancho propio y un final que deja la siguiente abierta |

## 6. Banco de temas con potencial de envío (público 18-30, España)
- **Vivienda**:
  - Cuánto hay que cobrar para alquilar sin ahogarse.
  - Cuánto ahorro hace falta para la entrada.
  - Compartir piso frente a vivir solo, en euros al año.
  - Cuánto subió el alquiler desde que tenías 18 años.
- **Sueldo**:
  - Bruto frente a neto con tu sueldo.
  - Qué se lleva cada parte de tu nómina.
  - El salario mínimo de 2026 en mano.
  - Pagas prorrateadas: ¿sí o no?
  - Primer sueldo: los 3 números que hay que mirar.
- **Gastos**:
  - Lo que cuestan de verdad las suscripciones (al año y en horas de trabajo).
  - El coste real del coche.
  - Comer fuera frente a llevar tupper en un año.
  - Black Friday: el descuento real.
- **Deuda**:
  - "Paga en 3 plazos sin intereses": cuándo sí y cuándo no.
  - Tarjeta revolving.
  - El préstamo para el móvil.
- **Impuestos**:
  - La declaración de la renta a los 20.
  - El mito del tramo del IRPF.
  - Qué pasa si vendes en Wallapop.
  - Cuánto se queda Hacienda de un premio.
- **Inversión**:
  - Interés compuesto con 50 € al mes desde los 20.
  - Comisiones de un fondo en 30 años.
  - Qué pasa si inviertes justo antes de una caída.
- **Actualidad**:
  - Euríbor.
  - BCE.
  - IPC frente a sueldo.
  - Bitcoin (solo explicar).
  - Grandes empresas como el caso Nvidia.
- **Generacional**:
  - Lo que podía comprar un sueldo en 2006 frente a 2026.
  - Edad media de emancipación.
  - Cuántos años de sueldo cuesta un piso.

## 7. Lenguaje del guion
- Tú directo, frases de 6-10 palabras, una idea por frase. Verbos de acción ("haz", "mira", "fíjate").
- Muletillas que funcionan (con medida): "Haz la cuenta.", "Ojo.", "Y aquí viene lo bueno.", "Pero.",
  "¿El resultado?", "De media.", "En tu bolsillo.".
- Números en letras en la voz (regla de la voz) y en cifras enormes en pantalla.
- Cero jerga sin explicar. Si sale una sigla (TAE, IRPF), en la misma frase va lo que significa para ti.
- Nada de introducciones ni despedidas largas. Si una frase se puede quitar sin perder la idea, se quita.

## 8. Caption (para los envíos y los comentarios)
1. Primera línea: palabra clave que se busca + la cifra del gancho ("Alquiler: necesitas 3.500 € netos para…").
2. 2-4 líneas de desarrollo con la cuenta y el matiz.
3. Una **pregunta concreta** que se responda en una palabra ("¿En tu ciudad cuánto pagas por m²?").
4. CTA de envío: "Envíaselo a quien…".
5. 3-5 hashtags específicos. Al final, la línea legal fija.

## 9. Medir y ajustar
- Pide a Pol cada semana, por Telegram (`stats:`), por cada Reel:
  - Reproducciones y tiempo medio de visualización.
  - % que pasa de 3 s.
  - Envíos, guardados y seguidores ganados.
- Lo que funcione se convierte en serie; lo que no pase de 3 s, cambia de gancho, no de tema.
- Prueba A/B barata: el mismo tema con dos ganchos distintos en días distintos.

## 10. Herramientas que ayudan
| Herramienta | Para qué |
|---|---|
| `reel_fx.py` | `"subtitulos": "grande"`, `"ritmo": true`, `data-chart`, `data-news`, `data-photo`, `count`, `stamp`, `type` (la cuenta escrita en pantalla) |
| `hyperframes-registry` | ~450 bloques: tipografía cinética, subtítulos animados, transiciones. Inspírate o pórtalos a una escena con GSAP (`TL(i)`) |
| `earshot` | Revisa `escucha.txt`: voz desde el segundo 0 y efectos sincronizados |
| `real-sfx` / `real-sound` | Efectos reales si los sintéticos se quedan cortos |
| `reverse-any-video` | Si Pol manda un Reel de referencia (archivo), reconstruir su estructura escena a escena y aplicarla con nuestros datos |
| `agent-reach` (solo lectura) | Leer YouTube, Reddit o X cuando el entorno tenga salida a esas webs; ahora no la tiene, se usa la búsqueda web |
| `skill-inspector` + `tools/scan_skills.py` | Escanear cualquier skill antes de instalarla (`docs/seguridad-skills.md`) |

Fuentes:
- [Reelxo, señales oficiales de Reels](https://www.reelxo.tech/blog/instagram-reels-algorithm)
- [Reeldrop, algoritmo de Reels 2026](https://www.reeldrop.io/blog/instagram-reels-algorithm/)
- [Emplifi, datos de Reels](https://emplifi.io/resources/facebook-reels-data/)
- [Socialinsider, duración de Reels](https://www.socialinsider.io/blog/instagram-reels-length/)
- [Revid, duración de Reels](https://www.revid.ai/blog/how-long-should-reel-be)
- [CapCut, pattern interrupts](https://www.capcut.com/create/pattern-interrupt-technique-short-form-video)
- Prensa sobre vídeos virales de sueldo y alquiler en España:
  - [Cronista](https://www.cronista.com/espana/economia-finanzas/una-joven-argentina-en-espana-se-decepciona-al-recibir-su-primer-sueldo-asegura-que-no-le-alcanza-ni-para-pagar-el-alquiler)
  - [Qué!](https://www.que.es/2026/06/06/trabajar-noruega-salario-asistente-infantil/)
