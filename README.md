# csf-media

Imágenes públicas de @capital.sin.filtros para la publicación automática en Instagram.
Cada carpeta de `posts/` coincide con el nombre de la carpeta en Google Drive y contiene las slides en JPG y `post.json` (caption + URLs).

## Flujo
1. Claude genera las slides (JPG) en `posts/<slug>/` y ejecuta `tools/build_post.py` (crea `post.json`).
2. Claude guarda el post en el data store de Make "CSF cola" (estado `pendiente`, caption y files) vía API.
3. Claude envía el álbum de revisión con `tools/send_review.py` (0 operaciones de Make).
4. Los botones de Telegram los procesa Make (escenario "Aprobar o rechazar", 2 operaciones).
5. Cada día a las 13:30 Make publica el post aprobado más antiguo (4 operaciones).

El token del bot nunca se guarda aquí: este repositorio es público.
