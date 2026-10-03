"""Soundtrack for the mother-targeted coloring-book ad (pure stdlib, deterministic).

Reuses the Mix palette from boyama-reklam/tools/muzik.py; every SFX time mirrors a tween in index.html.
Run from boyama-anne/: python3 tools/ses.py
"""
import os, sys, types

src = open(os.path.join(os.path.dirname(__file__), "../../boyama-reklam/tools/muzik.py")).read()
mod = types.ModuleType("muzik"); exec(src.split("# ---------------- Reklam 1")[0], mod.__dict__)
Mix = mod.Mix

m = Mix(20, 7)
m.music(0.0, 20.0, 0.8)
# S1 question + photo scan
m.pop(0.1, 0.2, 600)
m.tone(0.4, 1.6, 300, 0.09, 900, decay=0.5)
m.noise(0.4, 1.6, 0.045, 6000, 6000, "bell", hp=True)
for i in range(7): m.chime(0.5 + i * 0.22, 1318.5 + (i % 3) * 200, 0.06)
m.noise(2.6, 0.35, 0.16, 2500, 1200, "lin", hp=True)   # marker swipe under caption
# cuts
for t in (4.0, 8.0, 13.0, 16.5): m.whoosh(t, 0.6, 0.3, 500, 6000)
# S2 book + hero
m.flip(4.5)
m.boing(5.65); m.thump(6.2, 0.4)
for i in range(5): m.pop(5.75 + i * 0.08, 0.1, 1100 + i * 120)
m.chime(5.8, 1568, 0.12)
# S3 phone crossed, morph to crayon, colouring
m.scribble(8.3, 0.5, 0.2)
m.noise(9.0, 0.45, 0.14, 800, 3500, "bell", hp=True)
m.pop(10.0, 0.2, 500)
t = 10.6
for k in range(7):
    m.scribble(t, 0.18, 0.17)
    t += 0.38 if k else 0.5
for k in range(3): m.pop(11.0 + k * 0.5, 0.22, 700 + k * 120)
# S4 stars
for i in range(5): m.pop(13.6 + i * 0.09, 0.12, 900 + i * 90)
# S5 steps, stamp, CTA
for i in range(3): m.pop(16.9 + i * 0.4, 0.18, 650 + i * 100)
m.thump(18.3, 0.55)
m.chime(18.6, 1046.5, 0.16)
m.write("assets/audio/anne.wav")
