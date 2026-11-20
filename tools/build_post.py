#!/usr/bin/env python3
"""Genera posts/<slug>/post.json a partir de las imágenes y el caption.

Uso:
  python3 tools/build_post.py <slug> <caption.txt> [--images-from <slug_origen>]
  python3 tools/build_post.py <slug> <caption.txt> --reel      (usa posts/<slug>/reel.mp4 y cover.jpg)

- Las imágenes deben estar en posts/<slug>/01.jpg, 02.jpg... (JPG, 1080x1350).
- post.json contiene: caption, files (Instagram) y telegram_media (álbum de revisión).
"""
import json, sys, pathlib

REPO_RAW = "https://raw.githubusercontent.com/dineroaldescubierto15-blip/csf-media/main/posts"
# Vídeos: jsDelivr los sirve como video/mp4 (raw.githubusercontent los da como octet-stream)
CDN = "https://cdn.jsdelivr.net/gh/dineroaldescubierto15-blip/csf-media@main/posts"

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    slug, caption_path = args[0], args[1]
    src = args[args.index("--images-from") + 1] if "--images-from" in args else slug
    if "--reel" in args:
        root = pathlib.Path(__file__).resolve().parent.parent / "posts"
        if not (root / slug / "reel.mp4").exists():
            sys.exit(f"Falta posts/{slug}/reel.mp4")
        caption = pathlib.Path(caption_path).read_text(encoding="utf-8").strip()
        if len(caption) > 2200:
            sys.exit("El caption supera los 2200 caracteres de Instagram.")
        post = {"type": "reel", "slug": slug, "caption": caption,
                "video_url": f"{CDN}/{slug}/reel.mp4", "cover_url": f"{REPO_RAW}/{slug}/cover.jpg"}
        (root / slug / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"OK posts/{slug}/post.json (reel)")
        return
    if len(slug) > 55:
        sys.exit("El slug debe tener 55 caracteres o menos (límite de los botones de Telegram).")
    root = pathlib.Path(__file__).resolve().parent.parent / "posts"
    imgs = sorted(p.name for p in (root / src).glob("*.jpg"))
    if not 2 <= len(imgs) <= 10:
        sys.exit(f"Se necesitan entre 2 y 10 JPG en posts/{src}/ (hay {len(imgs)}).")
    urls = [f"{REPO_RAW}/{src}/{n}" for n in imgs]
    caption = pathlib.Path(caption_path).read_text(encoding="utf-8").strip()
    if len(caption) > 2200:
        sys.exit("El caption supera los 2200 caracteres de Instagram.")
    post = {
        "type": "carousel",
        "slug": slug,
        "caption": caption,
        "files": [{"media_type": "IMAGE", "image_url": u} for u in urls],
        "telegram_media": [{"type": "photo", "sendType": "send_byurl", "httpUrl": u} for u in urls],
    }
    out = root / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"OK posts/{slug}/post.json ({len(urls)} imágenes)")

if __name__ == "__main__":
    main()
