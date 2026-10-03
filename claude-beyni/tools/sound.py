"""Synthesize the soundtrack for "Claude'un Beyni" (pure stdlib, deterministic).

Every event time mirrors a tween in index.html. Run: python3 tools/sound.py
Writes assets/audio/beyin.wav (44.1 kHz, 16-bit, stereo).
"""
import math, random, struct, wave, os

SR = 44100
DUR = 60.0
N = int(SR * DUR)
L = [0.0] * N
R = [0.0] * N
rng = random.Random(1915)
TAU = 2 * math.pi


def put(i, v, pan=0.0):
    if 0 <= i < N:
        L[i] += v * (1 - max(0, pan))
        R[i] += v * (1 + min(0, pan))


def tone(t0, dur, f0, amp, f1=None, attack=0.005, kind="sine", pan=0.0, decay=None):
    f1 = f1 or f0
    n = int(dur * SR); s0 = int(t0 * SR); ph = 0.0
    for k in range(n):
        x = k / n
        f = f0 * (f1 / f0) ** x
        ph += TAU * f / SR
        env = min(1.0, k / (attack * SR + 1)) * (math.exp(-x * decay) if decay else (1 - x) ** 1.5)
        if kind == "sine": w = math.sin(ph)
        elif kind == "tri": w = 2 / math.pi * math.asin(math.sin(ph))
        else: w = 1.0 if math.sin(ph) > 0 else -1.0
        put(s0 + k, w * env * amp, pan)


def noise(t0, dur, amp, cut0, cut1, shape="bell", pan=0.0, hp=False):
    n = int(dur * SR); s0 = int(t0 * SR); y = 0.0; prev = 0.0
    for k in range(n):
        x = k / n
        cut = cut0 * (cut1 / cut0) ** x
        a = 1 - math.exp(-TAU * cut / SR)
        w = rng.uniform(-1, 1)
        y += a * (w - y)
        out = (y - prev) if hp else y
        prev = y
        if shape == "bell": env = math.sin(math.pi * x) ** 2
        elif shape == "hit": env = math.exp(-x * 9)
        else: env = (1 - x)
        put(s0 + k, out * env * amp, pan)


def click(t0, amp=0.18, pan=0.0):
    noise(t0, 0.012, amp * 3, 6000, 3000, "hit", pan, hp=True)
    tone(t0, 0.03, 1800 + rng.uniform(-200, 200), amp * 0.25, decay=18, pan=pan)


def whoosh(t0, dur, amp=0.55, low=300, high=5000):
    # rises into the cut, falls after it; centred on the transition
    noise(t0 - dur * 0.35, dur, amp, low, high, "bell", pan=-0.3)
    noise(t0 - dur * 0.30, dur, amp * 0.8, high, low, "bell", pan=0.3)


def impact(t0, amp=0.9):
    tone(t0, 1.4, 70, amp, 38, attack=0.002, decay=4.5)
    noise(t0, 0.35, amp * 0.6, 2500, 200, "hit")


def bell(t0, f, amp=0.22, pan=0.0):
    for m, a in ((1, 1.0), (2.01, 0.45), (3.0, 0.22), (4.2, 0.12)):
        tone(t0, 2.2, f * m, amp * a, attack=0.002, decay=3.5 + m, pan=pan)


def pad(t0, t1, freqs, amp, attack=1.5, release=1.5):
    s0, s1 = int(t0 * SR), int(t1 * SR)
    phs = [rng.uniform(0, TAU) for _ in freqs]
    for i in range(s0, min(N, s1)):
        t = (i - s0) / SR
        env = min(1, t / attack) * min(1, (t1 - i / SR) / release)
        lfo = 0.75 + 0.25 * math.sin(TAU * 0.13 * i / SR)
        v = 0.0
        for j, f in enumerate(freqs):
            v += math.sin(TAU * f * i / SR + phs[j]) + 0.3 * math.sin(TAU * f * 2.003 * i / SR)
        v *= amp * env * lfo / len(freqs)
        L[i] += v * (1.0 if j % 2 else 0.9); R[i] += v


# ---------------- bed ----------------
pad(0.0, 28.5, [55.0, 82.41, 110.0, 164.81], 0.20, attack=2.0)          # A minor-ish drone
pad(27.6, 39.4, [49.0, 73.42, 98.0, 146.83], 0.22, attack=1.0)          # darker during thinking
pad(38.8, 49.6, [55.0, 82.41, 110.0, 130.81, 164.81], 0.18, attack=0.6)  # tools
pad(48.8, 60.0, [65.41, 98.0, 130.81, 164.81, 196.0], 0.22, attack=1.2, release=1.4)  # warm C major for the answer

# ---------------- S1: soru ----------------
TOKENS = ["Çan", "akkale", " Savaşı", "'nı", " 20", " saniyede", " anlat"]
nch = sum(len(t) for t in TOKENS)
for k in range(nch):
    click(0.8 + k * 0.06, 0.14, pan=rng.uniform(-0.3, 0.3))
TYPED = 0.8 + nch * 0.06
tone(TYPED + 0.25, 0.25, 160, 0.5, 70, decay=8)            # send press
noise(TYPED + 0.25, 0.25, 0.25, 1200, 300, "hit")
for i in range(7):                                          # tokenize pops, rising
    tone(TYPED + 0.55 + i * 0.07, 0.18, 520 * 2 ** (i / 7), 0.18, kind="tri", decay=10, pan=-0.6 + i * 0.2)

# ---------------- transitions ----------------
T1, T2, T3, T4, T5 = 8, 17, 28, 39, 49
whoosh(T1 + 0.4, 1.1)
whoosh(T2 + 0.4, 1.1)
whoosh(T3 + 0.5, 1.6, amp=0.6, low=120, high=2500)          # gravitational lens: deep
tone(T3 + 0.3, 1.4, 90, 0.35, 45, attack=0.3, decay=2)
for k in range(9):                                          # glitch: digital stutter
    t = T4 + k * 0.065
    tone(t, 0.05, rng.choice([220, 440, 880, 1320, 1760]), 0.16, kind="sq", decay=6, pan=rng.uniform(-0.7, 0.7))
    noise(t, 0.04, 0.25, 7000, 4000, "hit", rng.uniform(-0.7, 0.7), hp=True)
whoosh(T5 + 0.5, 1.6, amp=0.45, low=800, high=9000)          # light leak: airy
for k, f in enumerate([1046.5, 1318.5, 1568.0]):
    tone(T5 + 0.35 + k * 0.09, 1.6, f, 0.06, attack=0.2, decay=2.5)

# ---------------- S2: token -> numbers ----------------
A2 = T1 + 0.3
for r in range(7):
    for c in range(0, 18, 3):
        click(A2 + 0.45 + r * 0.09 + c * 0.025, 0.06, pan=-0.8 + c / 11)
for k in range(10):                                         # number count blips
    tone(A2 + 1.7 + k * 0.13, 0.05, 1200 + k * 60, 0.05, decay=12)

# ---------------- S3: attention ----------------
A3 = T2 + 0.3
for i in range(7):
    tone(A3 + 0.2 + i * 0.07, 0.15, 660, 0.12, kind="tri", decay=10, pan=-0.8 + i * 0.27)
for k in range(6):                                          # lines drawing: soft glides
    tone(A3 + 1.1 + k * 0.12, 0.8, 300 + k * 40, 0.07, 600 + k * 80, attack=0.2)
bell(A3 + 2.2, 880, 0.14); bell(A3 + 2.35, 1046.5, 0.12)
t0 = A3 + 5.7
for n in range(2, 49):                                      # layer counter, accelerating
    click(t0 + 2.2 * math.sqrt((n - 1) / 47), 0.08, pan=rng.uniform(-0.4, 0.4))

# ---------------- S4: thinking ----------------
A4 = T3 + 0.5
LI = 1.35
for k in range(5):
    tone(A4 + 0.4 + k * LI, 0.3, 392, 0.08, kind="tri", decay=7)
noise(A4 + 0.4 + 2 * LI + 0.55, 0.45, 0.35, 3000, 900, "lin")   # strike-through scratch
bell(A4 + 0.4 + 3 * LI + 0.3, 659.25, 0.16)                       # accepted idea
for k in range(2):
    tone(A4 + 4.2 + k * 0.6, 0.25, 140, 0.3, 90, decay=10)          # rejected branches
bell(A4 + 5.6, 783.99, 0.16)

# ---------------- S5: tools ----------------
A5 = T4 + 0.3
TT = [A5 + 1.2, A5 + 2.4, A5 + 5.0, A5 + 6.4]
for t in TT[:3]:
    for k in range(4): click(t + k * 0.035, 0.1)
tone(TT[1] + 0.3, 2.2, 220, 0.08, 880, attack=0.2)                  # progress riser
tone(TT[2] + 0.2, 0.3, 300, 0.2, 600, decay=8)                      # thumbnail pop
bell(TT[3], 1046.5, 0.18); bell(TT[3] + 0.12, 1568.0, 0.14)         # success

# ---------------- S6: answer ----------------
A6 = T5 + 0.5
for base in (A6 + 0.6, A6 + 3.2):
    for k in range(3): tone(base + 0.2 + k * 0.08, 0.6, 330 + k * 30, 0.05, 520 + k * 50, attack=0.1)
    click(base + 1.1, 0.15)
impact(A6 + 2.4, 0.6); bell(A6 + 2.4, 523.25, 0.2)
impact(A6 + 5.0, 1.0); bell(A6 + 5.0, 659.25, 0.22); bell(A6 + 5.05, 783.99, 0.18)
noise(A6 + 5.6, 0.9, 0.12, 4000, 12000, "bell", hp=True)            # underline shimmer

# ---------------- master ----------------
fade_out = int(0.9 * SR)
peak = max(max(abs(v) for v in L), max(abs(v) for v in R)) or 1.0
g = 1.15 / peak
os.makedirs("assets/audio", exist_ok=True)
with wave.open("assets/audio/beyin.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    frames = bytearray()
    for i in range(N):
        f = 1.0
        if i < int(0.05 * SR): f = i / (0.05 * SR)
        if i > N - fade_out: f = (N - i) / fade_out
        l = math.tanh(L[i] * g) * 0.89 * f
        r = math.tanh(R[i] * g) * 0.89 * f
        frames += struct.pack("<hh", int(l * 32767), int(r * 32767))
    w.writeframes(bytes(frames))
print("wrote assets/audio/beyin.wav")
