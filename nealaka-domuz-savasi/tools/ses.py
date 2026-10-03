"""Soundtrack for the NeAlaka "Domuz Savaşı" short (pure stdlib, deterministic).
Comic oompah bed + SFX whose times mirror the tweens in index.html (beat starts in S).
Run from the project root: python3 tools/ses.py
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



S = [0.0, 3.6, 8.0, 12.4, 16.4, 20.6, 24.6, 29.6, 34.4, 38.6]
END = 43.0
m = Mix(END, 1859)

# oompah bed (F major), stops for the sad trombone
def oompah(start, end, g=0.6):
    beat = 60 / 126.0; hz = lambda n: 440 * 2 ** ((n - 69) / 12)
    prog = [(41, [65, 69, 72]), (36, [64, 67, 70]), (41, [65, 69, 72]), (36, [64, 67, 72])]
    b = 0
    while start + b * beat < end:
        t = start + b * beat; root, ch = prog[(b // 4) % 4]
        if b % 2 == 0:
            m.tone(t, beat * 0.9, hz(root + (0 if b % 4 == 0 else 7)), 0.42 * g, decay=5, kind="tri")
        else:
            for j, n in enumerate(ch): m.pluck(t + j * 0.01, hz(n), 0.12 * g, dur=beat * 0.5, bright=0.8)
            m.noise(t, 0.06, 0.05 * g, 8000, 6000, "hit", hp=True)
        if b % 4 == 3: m.pluck(t + beat / 2, hz(ch[-1] + 12), 0.08 * g, dur=beat * 0.5)
        b += 1
oompah(0.2, 38.4)

def slide(t, f0, f1, dur, a=0.18): m.tone(t, dur, f0, a, f1, decay=1.2, kind="sine", attack=0.02)
def gun(t): m.noise(t, 0.5, 0.9, 6000, 300, "hit"); m.tone(t, 0.6, 90, 0.8, 40, decay=5)
def horn(t, d=1.3):
    for f in (110, 138.6, 164.8): m.tone(t, d, f, 0.12, decay=1.0, kind="tri", attack=0.08)

for t in S[1:]: m.whoosh(t - 0.1, 0.6, 0.28, 500, 6000)   # page swaps
# B0
m.whoosh(0.4, 0.6, 0.25); slide(0.6, 1600, 300, 0.7); m.thump(1.3, 0.6); m.thump(1.5, 0.5); m.pop(2.0, 0.2, 700)
# B1
t = S[1]; m.pop(t + 0.5, 0.2, 600); m.scribble(t + 1.0, 0.4, 0.14); m.scribble(t + 1.6, 0.4, 0.14)
m.pop(t + 0.7, 0.15, 800); m.pop(t + 1.2, 0.15, 850); m.pop(t + 1.8, 0.15, 900); m.boing(t + 2.4); m.pop(t + 2.6, 0.18, 1000)
# B2
t = S[2]
for k in range(3): m.pop(t + 0.3 + k * 0.1, 0.12, 500 + k * 60)
m.whoosh(t + 0.6, 0.4, 0.2)
for k in range(10): m.noise(t + 1.0 + k * 0.17, 0.06, 0.16, 1800, 700, "hit")   # munching
m.whoosh(t + 1.8, 0.5, 0.25); gun(t + 3.0); slide(t + 3.1, 900, 200, 0.6, 0.15)
# B3
t = S[3]; m.thump(t + 1.5, 0.7); m.whoosh(t + 2.2, 0.4, 0.2); m.pop(t + 2.6, 0.2)
# B4
t = S[4]; m.pop(t + 0.4, 0.2)
for k in range(9): m.noise(t + 1.6 + k * 0.16, 0.08, 0.22, 3000, 1500, "hit", hp=True)  # marching snare
for k in range(10): m.pop(t + 2.4 + k * 0.08, 0.06, 1200 + k * 40)
m.thump(t + 2.4, 0.5)
# B5
t = S[5]; m.noise(t, 4.0, 0.06, 500, 900, "bell"); horn(t + 0.7); horn(t + 1.4, 1.0); m.pop(t + 1.8, 0.2, 600)
# B6
t = S[6]; m.whoosh(t + 0.4, 0.5, 0.25); m.pop(t + 1.0, 0.25, 500)
for k in range(12): m.pop(t + 0.8 + k * 0.1, 0.05, 1300)
for k in range(12): m.pop(t + 2.4 + k * 0.1, 0.05, 1500)
m.pop(t + 1.6, 0.2, 700); m.pop(t + 3.4, 0.2, 800); slide(t + 3.6, 400, 1400, 0.4, 0.12)
# B7
t = S[7]; m.whoosh(t + 0.5, 0.4, 0.2); m.pop(t + 1.1, 0.25, 600); slide(t + 2.4, 700, 250, 0.5, 0.12)
# B8
t = S[8]; m.pop(t + 0.9, 0.2); m.thump(t + 1.7, 0.6)
for tt in (t + 2.2, t + 2.5):
    m.noise(tt, 0.3, 0.45, 5000, 800, "hit")
    for k, f in enumerate((1046.5, 1318.5, 1568.0)): m.chime(tt + k * 0.07, f, 0.08)
for k in range(6): m.boing(t + 2.2 + k * 0.5, 0.12)
# B9: sad trombone, halo chime, sting
t = S[9]
for k, f in enumerate((233.1, 220.0, 207.7)): m.tone(t + 0.4 + k * 0.55, 0.5, f, 0.22, f * 0.98, decay=0.8, kind="tri", attack=0.03)
n = int(1.6 * SR); s0 = int((t + 2.05) * SR); ph = 0.0
for k in range(n):
    x = k / n; f = 196.0 * (1 + 0.03 * math.sin(2 * math.pi * 6 * k / SR)); ph += 2 * math.pi * f / SR
    m.put(s0 + k, (2 / math.pi * math.asin(math.sin(ph))) * 0.22 * min(1, k / 800) * (1 - x) ** 0.6)
m.chime(t + 1.2, 1568.0, 0.12)
m.kick(END - 1.8, 0.6); m.chime(END - 1.8, 1046.5, 0.16); m.chime(END - 1.75, 1318.5, 0.12)
m.write("assets/audio/domuz.wav")
