# Estadísticas automáticas de los Reels

El workflow `.github/workflows/stats-reels.yml` lee cada día (03:40 UTC) las métricas de los Reels con la API
oficial de Instagram y deja en `main`, **cifradas** (el repositorio es público; decisión de Pol, 25-11-2026):
- `stats/estadisticas.tar.enc` + `stats/estadisticas.clau.enc`, que contienen:
  - `reels.json`: todas las métricas por Reel (con su slug).
  - `resum.md`: tabla para leer rápido (duración, vista media, % visto, reproducciones, alcance, envíos, guardados…).

Cifrado híbrido con openssl (`tools/stats_crypto.py`): la clave pública está en `stats/clau_publica.pem`; la clave
privada, solo en el data store de Make (registro `config-stats`, campo `texto`). Nunca subas los archivos descifrados.
No gasta operaciones de Make. Solo métricas agregadas de los vídeos (nada de tokens ni datos de personas).

## Cómo se usa en la tarea diaria
1. `git pull`; si existe `stats/estadisticas.tar.enc`, lee la clave privada del registro `config-stats` del data store,
   guárdala en un archivo temporal FUERA del repo y descifra en el scratchpad:
   `STATS_PRIV="$(cat <archivo>)" python3 tools/stats_crypto.py descifrar <scratchpad>/stats` → lee `resum.md`.
2. Lo que retiene (% visto alto) y lo que se envía (envíos por 1.000 de alcance) marca qué formatos, ganchos y temas
   repetir; lo que no pasa de 3 s cambia de gancho, no de tema (`docs/viralidad.md`, sección 9).
3. Anota en el resumen final 1-2 conclusiones y qué has cambiado por ellas.

## Puesta en marcha (una vez, la hace Pol)
La cuenta tiene que ser profesional (empresa o creador), que ya lo es porque Make publica por la API.
1. Entra en https://developers.facebook.com → **Mis apps** → **Crear app**. Caso de uso: **Instagram** ("Administrar
   mensajes y contenido en Instagram"). Nombre: por ejemplo "CSF estadisticas". Tipo: empresa.
2. En la app: **Instagram → Configuración de la API con inicio de sesión de Instagram** → **Generar identificadores de
   acceso** → **Añadir cuenta** → entra con @capital.sin.filtros y acepta los permisos (incluido el de estadísticas,
   `instagram_business_manage_insights`).
3. Pulsa **Generar token** al lado de la cuenta y copia el token (empieza por `IG...`, dura 60 días).
4. En GitHub: repositorio `csf-media` → **Settings → Secrets and variables → Actions → New repository secret** →
   nombre `IG_TOKEN`, valor el token. (Nunca lo pegues en un archivo del repositorio: es público.)
5. **Actions → Estadísticas de los Reels → Run workflow** para probarlo. Deberían aparecer los archivos cifrados en `stats/`.

La app puede quedarse en modo desarrollo: solo lee la propia cuenta. El token caduca a los 60 días: si el workflow
falla con "token expired" o "Error validating access token", repite el paso 3 y actualiza el secreto.

Si el token es de inicio de sesión de Facebook (empieza por `EAA...`), añade también el secreto `IG_USER_ID`.
