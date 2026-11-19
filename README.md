# csf-media

Imágenes públicas de @capital.sin.filtros para la publicación automática en Instagram.
Cada carpeta de `posts/` coincide con el nombre de la carpeta en Google Drive y contiene las slides en JPG y `post.json` (caption + URLs).

## Flujo
1. Claude genera las slides (JPG) en `posts/<slug>/` y ejecuta `tools/build_post.py`.
2. Make envía el álbum a Telegram con botones Aprobar / Rechazar.
3. La aprobación se guarda en el data store de Make "CSF cola".
4. Cada día a las 13:30 Make publica el post aprobado más antiguo.
