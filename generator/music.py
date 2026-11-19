#!/usr/bin/env python3
"""Genera una base musical original (sin derechos de terceros) para los Reels.

Uso: python3 generator/music.py <segundos> <salida.wav> [--seed N] [--bpm 92]
Acordes suaves + bajo + percusión ligera, 48 kHz estéreo, con fade in/out.
La semilla cambia la progresión y el tempo para que cada Reel suene distinto.
"""
import sys, wave, random
import numpy as np

SR = 48000
PROGS = [
    [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)],   # Am F C G
    [(48, 52, 55), (55, 59, 62), (57, 60, 64), (53, 57, 60)],   # C G Am F
    [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)],   # Dm Bb F C
    [(52, 55, 59), (48, 52, 55), (55, 59, 62), (50, 54, 57)],   # Em C G D
]

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def env(n, a, r):
    e = np.ones(n)
    a, r = min(a, n // 2), min(r, n // 2)
    e[:a] = np.linspace(0, 1, a); e[n - r:] = np.linspace(1, 0, r)
    return e

def main():
    dur = float(sys.argv[1]); out = sys.argv[2]
    seed = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 1
    rnd = random.Random(seed)
    bpm = float(sys.argv[sys.argv.index("--bpm") + 1]) if "--bpm" in sys.argv else rnd.choice([84, 88, 92, 96])
    prog = PROGS[seed % len(PROGS)]
    n = int(dur * SR); t = np.arange(n) / SR
    L = np.zeros(n); R = np.zeros(n)
    beat = 60 / bpm; bar = beat * 4
    # pads
    i = 0; pos = 0.0
    while pos < dur:
        chord = prog[i % len(prog)]
        s, e = int(pos * SR), min(n, int((pos + bar) * SR))
        tt = t[s:e] - pos; seg = e - s
        pad = sum(0.6 * np.sin(2 * np.pi * hz(m) * tt) + 0.25 * np.sin(2 * np.pi * hz(m + 12) * tt + 0.3) for m in chord)
        pad *= env(seg, int(0.25 * SR), int(0.35 * SR)) * 0.05
        L[s:e] += pad * 0.9; R[s:e] += pad * 1.1
        bass = np.sin(2 * np.pi * hz(chord[0] - 12) * tt) * env(seg, 200, int(0.2 * SR)) * 0.09
        L[s:e] += bass; R[s:e] += bass
        # arpegio suave en corcheas
        for k in range(8):
            ns = s + int(k * beat / 2 * SR); ne = min(e, ns + int(beat / 2 * SR))
            if ns >= e: break
            m = chord[k % 3] + 12 + (12 if k % 4 == 3 else 0)
            ta = np.arange(ne - ns) / SR
            note = np.sin(2 * np.pi * hz(m) * ta) * np.exp(-ta * 6) * 0.035
            (L if k % 2 else R)[ns:ne] += note
        pos += bar; i += 1
    # percusión
    k = 0; pos = 0.0
    while pos < dur:
        s = int(pos * SR)
        if k % 4 in (0, 2):  # kick
            m = min(n - s, int(0.25 * SR)); tk = np.arange(m) / SR
            kick = np.sin(2 * np.pi * (55 + 90 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 12) * 0.22
            L[s:s + m] += kick; R[s:s + m] += kick
        m = min(n - s, int(0.05 * SR))  # hat
        hat = np.random.default_rng(seed + k).standard_normal(m) * np.exp(-np.arange(m) / SR * 80) * 0.018
        L[s:s + m] += hat; R[s:s + m] += hat
        pos += beat / (1 if k % 2 else 1); k += 1
    fade = env(n, int(1.0 * SR), int(1.5 * SR))
    st = np.stack([L * fade, R * fade], axis=1)
    st /= max(1e-9, np.abs(st).max()) / 0.7
    with wave.open(out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    print(f"OK {out} ({dur:.1f}s, {bpm:.0f} bpm, seed {seed})")

if __name__ == "__main__":
    main()
