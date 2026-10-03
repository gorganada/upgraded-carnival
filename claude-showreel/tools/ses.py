"""128 BPM electronic bed + hits for the 15 s reel (pure stdlib, deterministic).
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



END = 15.0
B = 60 / 128.0
CH = 4 * B
m = Mix(END, 128)
hz = lambda n: 440 * 2 ** ((n - 69) / 12)

def saw(t0, dur, f, amp, cutoff=1800, pan=0.0):
    n = int(dur * SR); s0 = int(t0 * SR); y = 0.0; a = 1 - math.exp(-2 * math.pi * cutoff / SR)
    for k in range(n):
        x = k / n; ph = (k * f / SR) % 1.0
        v = 2 * ph - 1; y += a * (v - y)
        env = min(1, k / 80) * (1 - x) ** 2
        m.put(s0 + k, y * amp * env, pan)

prog = [45, 41, 48, 43]   # Am F C G
for b in range(32):
    t = b * B
    if b < 30: m.kick(t, 0.75)
    m.noise(t + B / 2, 0.06, 0.09, 9000, 7000, "hit", 0.2, hp=True)          # off-beat hat
    for q in (0.25, 0.75): m.noise(t + q * B, 0.03, 0.04, 10000, 8000, "hit", -0.2, hp=True)
    if b % 2 == 1: m.clap(t, 0.32)
    root = prog[(b // 4) % 4]
    saw(t, B * 0.9, hz(root - 12), 0.32, 500)                                   # bass
    for j, iv in enumerate((0, 7, 12, 15 if root in (45,) else 16)):           # arp 16ths
        if b >= 4: saw(t + j * B / 4, B / 4 * 0.9, hz(root + 12 + iv), 0.09, 2600, pan=-0.4 + j * 0.25)
# chapter impacts + risers
for i in range(1, 8):
    t = i * CH
    m.noise(t - 0.45, 0.45, 0.10, 800, 9000, "lin", hp=True)                   # riser into the cut
    m.noise(t, 0.25, 0.35, 4000, 300, "hit")
    m.tone(t, 0.5, 110, 0.5, 40, decay=6)
# chapter-specific accents
m.chime(0.15, 1318.5, 0.08)
for k in range(4): m.pop(T + k * B if (T := CH) else 0, 0.18, 400 + k * 120)    # word slams
for k in range(3): m.tone(2 * CH + (k + 1) * B * 0.95, 0.3, 300 + k * 150, 0.16, 900 + k * 200, decay=4, kind="tri")  # morphs
m.noise(4 * CH, 0.9, 0.12, 2000, 9000, "bell", hp=True)                         # particle swarm
m.noise(4 * CH + 1.35, 0.5, 0.25, 6000, 600, "hit")                             # explosion
for k in range(7): m.pop(5 * CH + 0.15 + k * 0.07, 0.1, 500 + k * 90)          # bars
for h in (6 * CH + 0.05, 6 * CH + 0.85): m.boing(h + 0.1, 0.25); m.thump(h + 0.52, 0.5)
m.whoosh(7 * CH + 0.3, 0.6, 0.4, 300, 9000)
m.tone(14.2, 1.2, 55, 0.9, 30, decay=3); m.noise(14.2, 0.6, 0.5, 9000, 400, "hit")
for f in (440, 554.4, 659.3, 880): m.tone(14.2, 0.8, f, 0.06, decay=3, kind="tri")
m.write("assets/audio/reel.wav")
