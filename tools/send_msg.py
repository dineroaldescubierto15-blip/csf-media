#!/usr/bin/env python3
"""Envía un mensaje de texto a Pol por Telegram (borradores de comentarios, respuestas, informes).

Uso:
  CSF_TG_TOKEN=... CSF_TG_CHAT=... python3 tools/send_msg.py <archivo.txt | ->

El texto se envía tal cual (sin formato); si supera 4096 caracteres se parte en varios mensajes.
El token NUNCA se guarda en este repositorio (es público). No consume operaciones de Make.
"""
import json, os, sys, urllib.request

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    token, chat = os.environ.get("CSF_TG_TOKEN"), os.environ.get("CSF_TG_CHAT")
    if not token or not chat:
        sys.exit("Faltan CSF_TG_TOKEN / CSF_TG_CHAT")
    text = sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8").read()
    text = text.strip()
    if not text:
        sys.exit("Mensaje vacío")
    parts, cur = [], ""
    for para in text.split("\n\n"):
        if len(cur) + len(para) + 2 > 4000 and cur:
            parts.append(cur); cur = ""
        cur = (cur + "\n\n" + para) if cur else para
    parts.append(cur)
    for p in parts:
        req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
            data=json.dumps({"chat_id": chat, "text": p[:4096], "disable_web_page_preview": True}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            if not json.load(r).get("ok"):
                sys.exit("Telegram error")
    print(f"Mensaje enviado ({len(parts)} parte/s)")

if __name__ == "__main__":
    main()
