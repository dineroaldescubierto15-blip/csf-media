#!/usr/bin/env python3
"""Envía a Telegram el álbum de revisión de un post con botones Aprobar / Rechazar.

Uso:
  CSF_TG_TOKEN=... CSF_TG_CHAT=... python3 tools/send_review.py <slug> "<titulo>" ["<mensaje>"]

Lee posts/<slug>/post.json (generado con tools/build_post.py).
El token NUNCA se guarda en este repositorio (es público): se pasa por variable de entorno.
No consume operaciones de Make.
"""
import json, os, sys, pathlib, urllib.request, html

def api(token, method, payload):
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if not res.get("ok"):
        sys.exit(f"Telegram error en {method}: {res}")
    return res["result"]

def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    slug, titulo = sys.argv[1], sys.argv[2]
    mensaje = sys.argv[3] if len(sys.argv) > 3 else ""
    token, chat = os.environ.get("CSF_TG_TOKEN"), os.environ.get("CSF_TG_CHAT")
    if not token or not chat:
        sys.exit("Faltan CSF_TG_TOKEN / CSF_TG_CHAT")
    post = json.loads((pathlib.Path(__file__).resolve().parent.parent / "posts" / slug / "post.json").read_text())
    media = [{"type": "photo", "media": f["image_url"]} for f in post["files"]][:10]
    api(token, "sendMediaGroup", {"chat_id": chat, "media": media, "disable_notification": True})
    texto = f"<b>{html.escape(titulo)}</b>\n\n"
    if mensaje:
        texto += f"{html.escape(mensaje)}\n\n"
    texto += f"<b>Caption:</b>\n{html.escape(post['caption'])}"
    api(token, "sendMessage", {
        "chat_id": chat, "text": texto[:4096], "parse_mode": "HTML", "disable_web_page_preview": True,
        "reply_markup": {"inline_keyboard": [[
            {"text": "✅ Aprobar", "callback_data": f"ok:{slug}"},
            {"text": "❌ Rechazar", "callback_data": f"no:{slug}"}]]}})
    print(f"Aviso enviado: {slug}")

if __name__ == "__main__":
    main()
