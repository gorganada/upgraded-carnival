"""Soundtrack for the skill showcase (pure stdlib, deterministic). Times mirror index.html.
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



END = 20.6
m = Mix(END, 7)
m.music(0.0, END, 0.75)
# shot 1: title drops, scramble ticks, sparkle
for i in range(12):
    m.thump(1.2 + abs(i - 5.5) * 0.06 + 0.45, 0.18)
for k in range(20): m.pop(2.4 + k * 0.05, 0.05, 1500 + (k % 4) * 150)
m.chime(3.4, 1318.5, 0.12)
m.whoosh(5.4, 0.5, 0.2)
# iris + shot 2
m.whoosh(6.3, 0.8, 0.4, 300, 6000)
for t in (6.5, 7.7, 9.2, 10.7): m.noise(t, 0.3, 0.12, 1500, 5000, "bell", hp=True)
for t, f0, f1 in ((7.6, 300, 120), (9.1, 200, 500), (10.6, 400, 900)): m.tone(t, 0.7, f0, 0.22, f1, decay=2.5, kind="tri")
m.scribble(7.7, 0.8, 0.14)
m.noise(8.2, 0.8, 0.08, 7000, 9000, "lin", hp=True)          # fuse fizz
for k in range(4): m.kick(11.3 + k * 0.25, 0.35 if k % 2 == 0 else 0.25)   # heartbeat
m.whoosh(12.2, 0.6, 0.45, 300, 8000)
# shot 3: hops
for h in (12.8, 13.9, 15.0):
    m.tone(h, 0.14, 300, 0.12, 220, decay=6, kind="tri")            # anticipation creak
    m.boing(h + 0.14, 0.25)                                        # take-off
    m.thump(h + 0.69, 0.55)                                        # landing
    m.noise(h + 0.72, 0.3, 0.08, 1200, 400, "hit")                 # dust
for k in range(9): m.thump(16.2 + 0.45 + k * 0.05, 0.15)
m.chime(16.8, 1046.5, 0.12)
# shot 4
m.whoosh(17.9, 0.6, 0.35)
for k in range(7): m.pop(17.9 + k * 0.05 + 0.3, 0.12, 600 + k * 70)
m.noise(18.4, 0.6, 0.14, 2000, 6000, "bell", hp=True)
m.chime(19.1, 1046.5, 0.15); m.chime(19.16, 1568.0, 0.12)
m.write("assets/audio/vitrin.wav")
