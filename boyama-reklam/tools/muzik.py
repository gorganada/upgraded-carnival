"""Soundtracks for the three coloring-book ads (pure stdlib, deterministic).

Music: plucked (Karplus-Strong) C-G-Am-F loop at 112 BPM with a soft kick, clap and shaker.
SFX: every event time mirrors a tween in reklam-N/index.html.
Run from boyama-reklam/: python3 tools/muzik.py
"""
import math, random, struct, wave, os

SR = 44100
TAU = 2 * math.pi


class Mix:
    def __init__(self, dur, seed):
        self.n = int(dur * SR); self.L = [0.0] * self.n; self.R = [0.0] * self.n; self.rng = random.Random(seed); self.dur = dur

    def put(self, i, v, pan=0.0):
        if 0 <= i < self.n:
            self.L[i] += v * (1 - max(0, pan)); self.R[i] += v * (1 + min(0, pan))

    def pluck(self, t0, f, amp, dur=0.9, pan=0.0, bright=0.5):
        p = max(2, int(SR / f)); buf = [self.rng.uniform(-1, 1) for _ in range(p)]
        lp = 0.0
        for k in range(p):  # soften attack
            lp += bright * (buf[k] - lp); buf[k] = lp
        s0 = int(t0 * SR); idx = 0
        for k in range(int(dur * SR)):
            v = buf[idx]; nxt = buf[(idx + 1) % p]
            buf[idx] = 0.4985 * (v + nxt)
            idx = (idx + 1) % p
            env = 1.0 if k < SR * (dur - 0.08) else max(0.0, (dur * SR - k) / (0.08 * SR))
            self.put(s0 + k, v * amp * env, pan)

    def tone(self, t0, dur, f0, amp, f1=None, decay=6.0, kind="sine", pan=0.0, attack=0.003):
        f1 = f1 or f0; n = int(dur * SR); s0 = int(t0 * SR); ph = 0.0
        for k in range(n):
            x = k / n; f = f0 * (f1 / f0) ** x; ph += TAU * f / SR
            w = math.sin(ph) if kind == "sine" else (2 / math.pi * math.asin(math.sin(ph)))
            env = min(1.0, k / (attack * SR + 1)) * math.exp(-x * decay)
            self.put(s0 + k, w * env * amp, pan)

    def noise(self, t0, dur, amp, c0, c1, shape="hit", pan=0.0, hp=False):
        n = int(dur * SR); s0 = int(t0 * SR); y = 0.0; prev = 0.0
        for k in range(n):
            x = k / n; c = c0 * (c1 / c0) ** x; a = 1 - math.exp(-TAU * c / SR)
            y += a * (self.rng.uniform(-1, 1) - y); out = (y - prev) if hp else y; prev = y
            env = math.exp(-x * 7) if shape == "hit" else (math.sin(math.pi * x) ** 2 if shape == "bell" else 1 - x)
            self.put(s0 + k, out * env * amp, pan)

    # ---- sound palette ----
    def kick(self, t, a=0.55): self.tone(t, 0.32, 120, a, 45, decay=7)
    def clap(self, t, a=0.18): self.noise(t, 0.12, a, 2500, 1200, "hit", hp=True)
    def shaker(self, t, a=0.05): self.noise(t, 0.05, a, 9000, 7000, "hit", self.rng.uniform(-0.4, 0.4), hp=True)
    def pop(self, t, a=0.35, f=520): self.tone(t, 0.14, f, a, f * 2.2, decay=9)
    def thump(self, t, a=0.6): self.tone(t, 0.3, 140, a, 60, decay=9); self.noise(t, 0.1, a * 0.4, 1500, 300, "hit")
    def whoosh(self, t, dur=0.7, a=0.35, lo=400, hi=5000): self.noise(t - dur * 0.4, dur, a, lo, hi, "bell", -0.3); self.noise(t - dur * 0.35, dur, a * 0.7, hi, lo, "bell", 0.3)
    def chime(self, t, f=1046.5, a=0.16):
        for m, g in ((1, 1), (2.0, 0.4), (3.01, 0.2)): self.tone(t, 1.3, f * m, a * g, decay=4 + m)
    def scribble(self, t, dur=0.3, a=0.22):
        k = 0
        while k * 0.045 < dur:
            self.noise(t + k * 0.045, 0.04, a, 3500 + 900 * (k % 3), 2000, "hit", hp=True); k += 1
    def flip(self, t, a=0.4): self.noise(t, 0.35, a, 600, 6000, "bell", 0.2, hp=True); self.noise(t + 0.25, 0.12, a * 0.6, 1800, 500, "hit")
    def boing(self, t, a=0.3): self.tone(t, 0.45, 220, a, 660, decay=4, kind="tri")

    def music(self, start, end, gain=1.0):
        bpm = 112; beat = 60 / bpm
        chords = [[60, 64, 67], [55, 59, 62, 67], [57, 60, 64], [53, 57, 60, 65]]
        mel = [72, 74, 76, 79, 76, 74, 72, 69, 72, 76, 79, 81, 79, 76, 74, 72]
        hz = lambda m: 440 * 2 ** ((m - 69) / 12)
        b = 0
        while start + b * beat < end - 0.3:
            t = start + b * beat; bar = (b // 4) % 4; ch = chords[bar]
            for j, m in enumerate(ch):  # strum
                self.pluck(t + j * 0.018, hz(m), 0.16 * gain, dur=beat * 1.6, pan=-0.35 + j * 0.2)
            self.pluck(t, hz(ch[0] - 12), 0.22 * gain, dur=beat * 1.8, bright=0.3)
            if b % 2 == 0: self.kick(t, 0.38 * gain)
            else: self.clap(t, 0.12 * gain)
            for s in range(4): self.shaker(t + s * beat / 4, (0.05 if s % 2 else 0.035) * gain)
            if b % 2 == 1 or b % 8 == 0:
                self.pluck(t + beat / 2, hz(mel[b % 16]), 0.13 * gain, dur=beat, pan=0.3, bright=0.7)
            b += 1
        # final chord ring
        for j, m in enumerate([60, 64, 67, 72]): self.pluck(end - 2.2 + j * 0.03, hz(m), 0.16 * gain, dur=2.1)

    def write(self, path):
        peak = max(max(abs(v) for v in self.L), max(abs(v) for v in self.R)) or 1.0
        g = 1.1 / peak; fo = int(0.6 * SR)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with wave.open(path, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            fr = bytearray()
            for i in range(self.n):
                f = min(1.0, i / (0.03 * SR)) * (1.0 if i < self.n - fo else (self.n - i) / fo)
                fr += struct.pack("<hh", int(math.tanh(self.L[i] * g) * 0.89 * f * 32767), int(math.tanh(self.R[i] * g) * 0.89 * f * 32767))
            w.writeframes(bytes(fr))
        print("wrote", path)


# ---------------- Reklam 1: Fotoğraftan sayfaya ----------------
m = Mix(15, 1)
m.music(0.0, 15.0, 0.9)
for t in (0.15, 2.45, 3.7, 5.85): m.pop(t, 0.25, 600)
m.whoosh(0.6, 0.8, 0.3, 300, 3000); m.thump(1.15, 0.5)
m.scribble(1.1, 0.8, 0.12)                                  # caption handwriting
m.tone(2.6, 2.0, 300, 0.10, 900, decay=0.5)                 # scanner hum
m.noise(2.6, 2.0, 0.05, 6000, 6000, "bell", hp=True)
for i in range(9): m.chime(2.6 + max(0, min(1, (620 + i * 72 - 600) / 680)) * 2.0, 1318.5 + (i % 3) * 200, 0.07)
m.noise(4.1, 0.35, 0.18, 2500, 1200, "lin", hp=True)        # marker swipe
t = 5.3
for k in range(11):
    m.scribble(t + (0.5 if k == 0 else 0.26), 0.3, 0.2)
    t += 0.9 if k == 0 else 0.46
m.whoosh(11.7, 0.9, 0.35)
m.thump(11.9, 0.45); m.pop(12.05, 0.25); m.pop(12.5, 0.3, 700); m.chime(12.55, 1046.5, 0.15)
m.write("reklam-1/assets/audio/reklam-1.wav")

# ---------------- Reklam 2: Kahraman sensin ----------------
m = Mix(15, 2)
m.music(0.0, 15.0, 0.85)
for t in (0.15, 0.75, 1.35): m.kick(t, 0.6); m.pop(t, 0.2, 400)
m.noise(1.85, 0.45, 0.15, 1500, 4000, "bell", hp=True)
m.boing(1.9)
for i in range(6): m.pop(0.2 + i * 0.12, 0.12, 900 + i * 80)
m.whoosh(3.05, 0.6, 0.45, 600, 8000)
m.thump(3.3, 0.45); m.chime(3.7, 1318.5, 0.16)
for t in (4.8, 6.9, 9.0): m.flip(t)
for a in (5.4, 7.5, 9.6):
    for k in range(9): m.scribble(a + k * 0.15, 0.08, 0.1)
for t in (5.3, 7.4, 9.5): m.pop(t, 0.18, 700)
m.whoosh(11.7, 0.9, 0.35, 300, 4000)
m.thump(11.9, 0.45); m.pop(12.05, 0.25); m.pop(12.5, 0.3, 700); m.chime(12.55, 1046.5, 0.15)
m.write("reklam-2/assets/audio/reklam-2.wav")

# ---------------- Reklam 3: 3 adımda hediye ----------------
m = Mix(15, 3)
m.music(0.0, 15.0, 0.85)
m.pop(0.1, 0.2); m.thump(0.75, 0.5)
for k in range(10): m.noise(1.2 + k * 0.08, 0.05, 0.12, 2200, 900, "hit")  # gift rattle
m.pop(0.9, 0.2, 800); m.pop(1.1, 0.2, 900)
m.whoosh(3.0, 0.7, 0.35)
for t in (3.0, 5.55, 8.05): m.kick(t, 0.5); m.pop(t + 0.1, 0.2, 600)
m.pop(3.7, 0.2, 800); m.tone(4.0, 0.9, 400, 0.08, 1200, decay=0.6); m.chime(4.9, 1318.5, 0.15)
for i in range(6): m.pop(5.9 + i * 0.09, 0.14, 700 + i * 60)
m.chime(6.9, 1568.0, 0.16)
m.whoosh(8.6, 0.6, 0.3); m.thump(8.95, 0.45); m.pop(8.9, 0.18); m.thump(9.5, 0.7)
m.noise(10.5, 0.6, 0.12, 4000, 12000, "bell", hp=True)     # flash shimmer
m.thump(10.9, 0.45)
for k in range(6): m.noise(10.95 + k * 0.07, 0.05, 0.12, 2200, 900, "hit")
m.whoosh(11.6, 0.6, 0.3); m.noise(11.45, 0.3, 0.5, 5000, 800, "hit")       # popper
for k, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)): m.chime(11.5 + k * 0.08, f, 0.12)
m.pop(12.3, 0.2); m.pop(12.6, 0.3, 700)
m.write("reklam-3/assets/audio/reklam-3.wav")
