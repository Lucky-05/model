#!/usr/bin/env python3
"""Figures for Report 1. Uses ONLY the training recordings (the test recordings stay closed).

Needs numpy, scipy and matplotlib.   Run from the repository root:  python3 code/make_figures.py

Labels: we had no cue video on 19 Nov, so the only label is the KICK event that the board wrote
when its own threshold detector fired. Movement = 0.25 s windows that touch [KICK-0.25 s, KICK+0.25 s].
Rest = windows more than 1.5 s away from every KICK. Everything in between has no label.
"""
import csv, os, sys
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.join(os.path.dirname(__file__), "..")
TRAIN = ["2026-11-19_105551_p3", "2026-11-19_110757_p4"]      # two of the three training recordings
CH = "canal2"                                                 # the channel that carried the muscle signal
FS, WIN = 1000, 250

def load(name):
    with open(os.path.join(ROOT, "data", "raw", name + "_senal.csv")) as f:
        x = np.array([float(r[CH]) for r in csv.DictReader(f)])
    with open(os.path.join(ROOT, "data", "raw", name + "_eventos.csv")) as f:
        k = np.array([int(r["muestra"]) for r in csv.DictReader(f) if r["tipo"] == "KICK" and r["valor"] == CH[-1]])
    return x, k

def clean(x):
    b, a = signal.butter(4, [20, 450], btype="bandpass", fs=FS)
    y = signal.filtfilt(b, a, x)
    b, a = signal.iirnotch(60, 30, fs=FS)
    return signal.filtfilt(b, a, y)

def windows(x, k):
    y = clean(x); feats, labels = [], []
    for s in range(0, len(y) - WIN + 1, WIN):
        mid = s + WIN / 2
        d = np.min(np.abs(k - mid)) if len(k) else 1e9
        lab = 1 if d <= 250 + WIN / 2 else (0 if d > 1500 else None)
        if lab is None: continue
        w = y[s:s + WIN]
        feats.append([np.mean(np.abs(w)), np.sum(np.abs(np.diff(w)))]); labels.append(lab)
    return np.array(feats), np.array(labels)

# Figure 1: one recording with the detected contractions marked
x, k = load(TRAIN[1]); t = np.arange(len(x)) / FS
fig, ax = plt.subplots(2, 1, figsize=(11, 5), sharex=True)
ax[0].plot(t, x, lw=0.4, color="#1f4e79"); ax[0].set_ylabel("raw (counts, 0-1023)")
ax[1].plot(t, clean(x), lw=0.4, color="#1f4e79"); ax[1].set_ylabel("band-pass + notch"); ax[1].set_xlabel("seconds")
for a in ax:
    for kk in k: a.axvspan((kk - 250) / FS, (kk + 250) / FS, color="#d95f02", alpha=0.25, lw=0)
ax[0].set_title(TRAIN[1] + ", channel 2. Orange: 0.5 s around each KICK event of the board")
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "one_recording_marked.png"), dpi=130)

# Figure 2: two features, movement against rest, training recordings only
fig, ax = plt.subplots(figsize=(6.5, 5)); data = {}
for name, mk in zip(TRAIN, "o^"):
    F, L = windows(*load(name)); data[name] = (F, L)
    ax.scatter(F[L == 0, 0], F[L == 0, 1], s=12, marker=mk, color="#7f7f7f", alpha=0.5, label=f"rest, {name[-2:]}")
    ax.scatter(F[L == 1, 0], F[L == 1, 1], s=22, marker=mk, color="#d95f02", alpha=0.8, label=f"movement, {name[-2:]}")
    print(f"{name}: {int((L == 1).sum())} movement windows, {int((L == 0).sum())} rest windows; "
          f"median MAV movement {np.median(F[L == 1, 0]):.2f}, rest {np.median(F[L == 0, 0]):.2f}")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("mean absolute value (counts)"); ax.set_ylabel("waveform length (counts)")
ax.set_title("Windows of 0.25 s, training recordings only"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "two_features.png"), dpi=130)

# One threshold on MAV, set on the first training recording and checked on the second
(Fa, La), (Fb, Lb) = data[TRAIN[0]], data[TRAIN[1]]
thr = np.sqrt(np.median(Fa[La == 1, 0]) * np.median(Fa[La == 0, 0]))
for nm, F, L in ((TRAIN[0], Fa, La), (TRAIN[1], Fb, Lb)):
    p = F[:, 0] > thr
    print(f"threshold {thr:.2f} on {nm}: movement found {np.mean(p[L == 1]):.0%}, rest found {np.mean(~p[L == 0]):.0%}")
