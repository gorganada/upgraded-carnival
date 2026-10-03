"""Loopable 120 BPM bed for the coloring-book viral loop (pure stdlib, deterministic).
No fade in/out: the tail of the last bar wraps onto the head so the file loops seamlessly.
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


END = 15.0
B = 0.5
m = Mix(END, 77)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

def pad(t0, dur, notes, amp):
    n = int(dur * SR); s0 = int(t0 * SR)
    for k in range(n):
        x = k / n; env = math.sin(math.pi * x) ** 1.5
        v = sum(math.sin(2 * math.pi * hz(nn) * (s0 + k) / SR) + 0.3 * math.sin(2 * math.pi * hz(nn) * 2.003 * (s0 + k) / SR) for nn in notes)
        m.put(s0 + k, v * amp * env / len(notes))

for b in range(30):
    t = b * B
    m.kick(t, 0.7 if t < 2 or t >= 4.5 else 0.5)
    m.noise(t + B / 2, 0.05, 0.08, 9000, 7000, "hit", 0.25, hp=True)
    if b % 2 == 1: m.clap(t, 0.28)
    for q in range(4):
        m.pluck(t + q * B / 4, hz([72, 76, 79, 84, 79, 76, 74, 79][(b * 4 + q) % 8] + (12 if 9 <= t < 12 else 0)), 0.06, dur=0.3, bright=0.6, pan=-0.5 + q * 0.33)
for k, ch in enumerate([[48, 52, 55], [55, 59, 62], [57, 60, 64], [53, 57, 60]] * 2):
    if k * 2.0 < END: pad(k * 2.0, 2.2, ch, 0.16)
# hits on the cuts, risers into them
for t in (2.0, 4.0, 6.5, 9.0):
    m.noise(t - 0.4, 0.4, 0.09, 800, 9000, "lin", hp=True); m.noise(t, 0.2, 0.3, 4000, 300, "hit"); m.tone(t, 0.4, 100, 0.45, 40, decay=6)
m.noise(0.2, 0.8, 0.10, 2000, 8000, "bell", hp=True)            # crayon dust gathering into the name
m.noise(1.72, 0.3, 0.25, 6000, 500, "hit")
for k in range(4): m.pop(2.0 + k * B, 0.16, 520 + k * 80)       # word punches
m.scribble(4.05, 0.6, 0.18)                                      # the page draws itself
for k in range(6): m.pop(5.0 + k * B / 2, 0.14, 600 + k * 90)   # colour floods
for i in range(16): m.flip(6.5 + i * 0.13 + 0.3, 0.12)           # flip-book pages
m.noise(9.0, 0.9, 0.10, 2000, 8000, "bell", hp=True)
m.noise(11.6, 1.6, 0.07, 6000, 1500, "bell", hp=True)
m.chime(12.4, 1046.5, 0.12); m.chime(12.48, 1318.5, 0.1)

# loop-safe write: wrap the overhang of the last notes onto the start, no fades
peak = max(max(abs(v) for v in m.L), max(abs(v) for v in m.R)) or 1.0
g = 1.05 / peak
os.makedirs("assets/audio", exist_ok=True)
with wave.open("assets/audio/boyaviral.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    fr = bytearray()
    for i in range(m.n):
        fr += struct.pack("<hh", int(math.tanh(m.L[i] * g) * 0.89 * 32767), int(math.tanh(m.R[i] * g) * 0.89 * 32767))
    w.writeframes(bytes(fr))
print("wrote assets/audio/boyaviral.wav")
