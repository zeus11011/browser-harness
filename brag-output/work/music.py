"""120 BPM, A minor, 20s. Music + SFX on one grid (beat = 0.5s). Writes music.wav."""
import numpy as np, wave

SR, DUR, B = 44100, 20.0, 0.5
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    s = sig[: j - i] * gain
    L[i:j] += s * (1 - pan) ** .5 if pan > 0 else s
    R[i:j] += s * (1 + pan) ** .5 if pan < 0 else s

def env(n, a, d):  # attack, exp decay (seconds)
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

def tone(f, dur, a=.005, d=.3, harm=(1,), shape=None):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) / k for k in harm)
    return s * env(n, a, d)

def lp(x, k):  # one-pole lowpass
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y

def kick():
    n = int(.4 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / .03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16)

def noise(dur, d, hp=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    if hp: x = np.diff(np.concatenate([[0], x]))
    return x * env(n, .001, d)

CH = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [62, 67, 71])]  # Am F C G
K, Hh, Cl = kick(), noise(.08, .02), lp(noise(.25, .07, False), .35)

for bar in range(10):
    t0 = bar * 2
    root, chord = CH[bar % 4]
    full = 1 <= bar <= 8
    # pad
    if bar < 9 or True:
        pad = sum(tone(hz(m), 2.05, a=.25, d=3, harm=(1, 2, 3)) for m in chord)
        add(lp(pad, .06), t0, .05 if bar < 9 else .07)
    for b in range(4):
        tb = t0 + b * B
        if bar <= 8 or (bar == 9 and b == 0 and False):
            add(K, tb, .9 if full else .55)
        if full and b in (1, 3): add(Cl, tb, .22)
        if bar <= 8: add(Hh, tb + B / 2, .09 if full else .05, pan=.3)
        # bass: root on 8ths, offbeat pumped
        if bar <= 8:
            for e in range(2):
                add(lp(tone(hz(root - 12), .22, a=.004, d=.12, harm=(1, 2, 3)), .15), tb + e * B / 2, .32 if e else .22)
    # arp 16ths, plucky
    if bar <= 8:
        seq = [chord[0], chord[1], chord[2], chord[1] + 12, chord[2], chord[1], chord[0] + 12, chord[1]]
        for s16 in range(16):
            m = seq[s16 % 8]
            add(lp(tone(hz(m), .2, a=.002, d=.08, harm=(1, 2)), .25), t0 + s16 * B / 4, .06, pan=(-.4 if s16 % 2 else .4))

# ---- SFX, same key, on the 16th grid ----
for k in range(13):  # typing ticks 0.625..2.125
    add(lp(noise(.03, .006), .5), .625 + k * .125, .05, pan=.2)
pent = [69, 72, 74, 76, 79, 81, 84, 86]
for i, m in enumerate(pent):  # step cascade 3.25 + i*0.125
    add(tone(hz(m), .3, a=.002, d=.12, harm=(1, 3)), 3.25 + i * .125, .07)
for t in (6.0, 6.5, 7.0, 7.5, 8.0, 8.75, 9.5):  # executor step blips
    add(tone(hz(81), .12, a=.002, d=.04), t, .05)
for t in (7.875, 9.25):  # mouse clicks
    add(lp(noise(.04, .008), .6), t, .12)
add(tone(hz(33), .6, a=.003, d=.25, harm=(1, 2)) + tone(hz(46), .6, d=.15) * .3, 10.5, .45)  # fail: A1 thud + Bb tension
add(tone(hz(45), .5, a=.003, d=.2, harm=(1, 2, 3)), 11.0, .35)  # retry stamp
add(lp(noise(.2, .05, False), .3), 11.0, .2)
add(tone(hz(81), .9, d=.4, harm=(1, 2)) + tone(hz(88), .9, d=.4), 12.5, .1)  # pass chime A5+E6
add(lp(noise(.2, .05, False), .3), 12.5, .18)
n = int(1.0 * SR); t = np.arange(n) / SR  # riser into logo 16.0 -> 17.0
add(lp(rng.standard_normal(n), .02) * np.linspace(0, 1, n) ** 2 * 4 + np.sin(2 * np.pi * np.cumsum(220 + 660 * (t)) / SR) * (t ** 2) * .3, 16.0, .12)
# logo hit 17.0: big Am chord ring-out + kick + soft crash
add(K, 17.0, 1.0)
add(lp(noise(2.5, .8), .4), 17.0, .12)
add(sum(tone(hz(m), 3.0, a=.005, d=1.2, harm=(1, 2, 3)) for m in (45, 57, 64, 69, 72, 76)), 17.0, .08)

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.2)
fade = np.ones(N); fn = int(1.0 * SR); fade[-fn:] = np.linspace(1, 0, fn)
mix *= fade[:, None]
mix /= np.abs(mix).max() / 0.89
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("ok")
