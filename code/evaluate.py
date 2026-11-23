#!/usr/bin/env python3
"""Train, validate and test the first model, and draw the results.

Needs numpy, scipy, scikit-learn and matplotlib.   Run from the repository root:  python3 code/evaluate.py
WARNING: this script READS THE TEST RECORDINGS (set = test). It was run for the first time on 2026-11-23.
Writes RESULTS.md and figures/results_*.png.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
sys.path.insert(0, os.path.dirname(__file__))
from train_model import ROOT, FS, WIN, recordings, load, clean, windows, Threshold

def scores(L, p):
    tn, fp, fn, tp = confusion_matrix(L, p, labels=[0, 1]).ravel()
    return dict(n=len(L), acc=(tp + tn) / len(L), bal=balanced_accuracy_score(L, p),
                mov=tp / (tp + fn) if tp + fn else float("nan"), rest=tn / (tn + fp), tn=tn, fp=fp, fn=fn, tp=tp)

def row(name, s):
    return (f"| {name} | {s['n']} | {s['acc']:.0%} | {s['bal']:.0%} | {s['mov']:.0%} ({s['tp']}/{s['tp'] + s['fn']}) "
            f"| {s['rest']:.0%} ({s['tn']}/{s['tn'] + s['fp']}) |")

train, test = recordings("train"), recordings("test")
data = {n: windows(n) for n in train + test}
stack = lambda names: (np.vstack([data[n][0] for n in names]), np.concatenate([data[n][1] for n in names]))
HEAD = "| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |\n|---|---|---|---|---|---|"
out = ["# Results of the first model", "",
       "Made with `python3 code/evaluate.py`. Model: one threshold on the mean absolute value of a window of 0.25 s.",
       "Balanced accuracy is the mean of \"movement found\" and \"rest found\". We use it because there is about 4 times more rest than movement.", ""]

Ft, Lt = stack(train); model = Threshold().fit(Ft, Lt); thr = float(np.exp(model.t) - 0.1)
out += [f"## 1. Training (the model sees these windows)", "", f"Threshold: {thr:.2f} counts.", "", HEAD]
for n in train: out.append(row(n[-2:], scores(data[n][1], model.predict(data[n][0]))))
s_train = scores(Lt, model.predict(Ft)); out += [row("all", s_train), ""]

out += ["## 2. Validation (leave one training recording out)", "",
        "Each row: the threshold is set with the other two recordings, then checked on this one.", "", HEAD]
yt, yp = [], []
for o in train:
    F, L = stack([n for n in train if n != o]); p = Threshold().fit(F, L).predict(data[o][0])
    out.append(row(o[-2:], scores(data[o][1], p))); yt.append(data[o][1]); yp.append(p)
s_val = scores(np.concatenate(yt), np.concatenate(yp)); out += [row("all", s_val), ""]

out += ["## 3. Test (recordings the model never saw: p5 and p6)", "", HEAD]
for n in test: out.append(row(n[-2:], scores(data[n][1], model.predict(data[n][0]))))
Fe, Le = stack(test); pe = model.predict(Fe); s_test = scores(Le, pe); out += [row("all", s_test), ""]

# Figures
fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
for a, (t, s) in zip(ax, (("Training", s_train), ("Validation", s_val), ("Test", s_test))):
    m = np.array([[s["tn"], s["fp"]], [s["fn"], s["tp"]]]); a.imshow(m, cmap="Blues")
    for i in range(2):
        for j in range(2): a.text(j, i, m[i, j], ha="center", va="center", fontsize=14, color="white" if m[i, j] > m.max() / 2 else "black")
    a.set_xticks([0, 1]); a.set_xticklabels(["rest", "movement"]); a.set_yticks([0, 1]); a.set_yticklabels(["rest", "movement"])
    a.set_xlabel("model says"); a.set_ylabel("label"); a.set_title(f"{t}: balanced accuracy {s['bal']:.0%}")
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_confusion.png"), dpi=130)

fig, ax = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True); bins = np.logspace(-0.7, 1.5, 40)
for a, (t, F, L) in zip(ax, (("Training", Ft, Lt), ("Test", Fe, Le))):
    mav = np.exp(F[:, 0]) - 0.1
    a.hist(mav[L == 0], bins, color="#7f7f7f", alpha=0.7, label="rest"); a.hist(mav[L == 1], bins, color="#d95f02", alpha=0.7, label="movement")
    a.axvline(thr, color="k", ls="--", label=f"threshold {thr:.2f}"); a.set_xscale("log"); a.set_title(t)
    a.set_xlabel("mean absolute value of the window (counts)"); a.legend()
ax[0].set_ylabel("windows"); fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_histogram.png"), dpi=130)

fig, ax = plt.subplots(len(test), 1, figsize=(11, 2.8 * len(test)))
for a, n in zip(np.atleast_1d(ax), test):
    x, k = load(n); y = clean(x); nw = len(y) // WIN
    mav = np.abs(y[:nw * WIN]).reshape(nw, WIN).mean(axis=1); t = (np.arange(nw) + 0.5) * WIN / FS
    a.fill_between(t, 0, mav.max() * (mav > thr), step="mid", color="#d95f02", alpha=0.25, lw=0, label="model says movement")
    a.plot(t, mav, color="#1f4e79", lw=0.9, label="mean absolute value"); a.axhline(thr, color="k", ls="--", lw=0.8)
    a.plot(k / FS, np.full(len(k), mav.max() * 1.03), "v", color="k", ms=5, label="KICK event of the board")
    a.set_title(f"Test recording {n[-2:]}: every window of 0.25 s"); a.set_ylabel("counts"); a.legend(fontsize=7, loc="upper right", ncol=3)
np.atleast_1d(ax)[-1].set_xlabel("seconds"); fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_test_timeline.png"), dpi=130)

out += ["## What this shows", "",
        "- Training 95 %, validation 86 %, test 64 % (balanced accuracy). The goal is more than 75 % on recordings never seen. p5 passes (87 %), p6 does not (56 %).",
        "- Why p6 fails: its signal at rest is about 3.3 counts, above the threshold of 2.93, so the model says movement almost all the time. In p3 to p5 rest is 0.7 to 1.9 counts. One fixed threshold does not survive a change of the rest level.",
        "- The labels of p6 are also wrong: the figure shows about 12 contractions, and the board wrote only 2 KICK events. Windows inside real contractions count as rest here. So the true score of p6 is unknown.",
        "- The test recordings were opened on 2026-11-23. We do not tune the model on them. They are from the same session as the training recordings, so the final test will be new sessions with new electrodes.",
        "- Next: labels from a cue video instead of the board, and a size measured against the rest level of each recording (a short calibration at rest), checked with validation only.", ""]
out += ["## Figures", "", "- `figures/results_confusion.png`: right and wrong answers in training, validation and test.",
        "- `figures/results_histogram.png`: the size of the windows of each class and the threshold.",
        "- `figures/results_test_timeline.png`: what the model says along each test recording.", ""]
open(os.path.join(ROOT, "RESULTS.md"), "w").write("\n".join(out))
print("\n".join(out))
