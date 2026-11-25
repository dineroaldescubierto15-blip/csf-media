#!/usr/bin/env python3
"""Cifra y descifra las estadísticas de los Reels (el repositorio es público).

Cifrado híbrido con openssl: una clave AES-256 aleatoria cifra los archivos y esa clave se cifra con la clave PÚBLICA
RSA de stats/clau_publica.pem (puede estar en el repo). Solo la clave PRIVADA la descifra; está en el data store de
Make (registro `config-stats`, campo `texto`), nunca en el repositorio.

  python3 tools/stats_crypto.py cifrar <carpeta_con_reels.json_y_resum.md>
      -> stats/estadisticas.tar.enc + stats/estadisticas.clau.enc
  STATS_PRIV="$(cat clave.pem)" python3 tools/stats_crypto.py descifrar <carpeta_destino_fuera_del_repo>
      -> <destino>/reels.json y <destino>/resum.md
"""
import os, sys, pathlib, subprocess, tempfile, tarfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ST = ROOT / "stats"
PUB = ST / "clau_publica.pem"
ENC = ST / "estadisticas.tar.enc"
KEY = ST / "estadisticas.clau.enc"
FILES = ("reels.json", "resum.md")

def run(*a):
    subprocess.run(a, check=True, capture_output=True)

def cifrar(src):
    src = pathlib.Path(src)
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        tar = td / "s.tar"
        with tarfile.open(tar, "w") as t:
            for f in FILES:
                if (src / f).exists():
                    t.add(src / f, arcname=f)
        k = td / "k"; k.write_text(os.urandom(32).hex())
        run("openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt", "-pass", f"file:{k}", "-in", str(tar), "-out", str(ENC))
        run("openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", str(PUB), "-pkeyopt", "rsa_padding_mode:oaep",
            "-pkeyopt", "rsa_oaep_md:sha256", "-in", str(k), "-out", str(KEY))
    print(f"OK: {ENC.relative_to(ROOT)} y {KEY.relative_to(ROOT)}")

def descifrar(dst):
    priv = os.environ.get("STATS_PRIV", "")
    if "PRIVATE KEY" not in priv:
        sys.exit("Falta STATS_PRIV (clave privada del data store, registro config-stats).")
    dst = pathlib.Path(dst).resolve()
    if ROOT in dst.parents or dst == ROOT:
        sys.exit("Descifra fuera del repositorio (es público).")
    dst.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        pk = td / "p.pem"; pk.write_text(priv); pk.chmod(0o600)
        k = td / "k"; tar = td / "s.tar"
        run("openssl", "pkeyutl", "-decrypt", "-inkey", str(pk), "-pkeyopt", "rsa_padding_mode:oaep",
            "-pkeyopt", "rsa_oaep_md:sha256", "-in", str(KEY), "-out", str(k))
        run("openssl", "enc", "-d", "-aes-256-cbc", "-pbkdf2", "-pass", f"file:{k}", "-in", str(ENC), "-out", str(tar))
        with tarfile.open(tar) as t:
            for m in t.getmembers():
                if m.name in FILES:
                    t.extract(m, dst, filter="data")
    print(f"OK: descifrado en {dst}")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("cifrar", "descifrar"):
        sys.exit(__doc__)
    (cifrar if sys.argv[1] == "cifrar" else descifrar)(sys.argv[2])
