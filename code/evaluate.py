#!/usr/bin/env python3
"""Train, validate and test the model, and draw the results.

Needs numpy, scipy, scikit-learn and matplotlib.   Run from the repository root:  python3 code/evaluate.py
WARNING: this script READS THE TEST RECORDING (set = test). The test was first opened on 2026-11-23.
Writes RESULTS.md and figures/results_*.png.
"""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
sys.path.insert(0, os.path.dirname(__file__))
from train_model import ROOT, FS, WIN, MODELS, CHOSEN, recordings, load, window_sizes, windows, validate

def scores(L, p):
    tn, fp, fn, tp = confusion_matrix(L, p, labels=[0, 1]).ravel()
    return dict(n=len(L), acc=(tp + tn) / len(L), bal=balanced_accuracy_score(L, p),
                mov=tp / (tp + fn) if tp + fn else float("nan"), rest=tn / (tn + fp), tn=tn, fp=fp, fn=fn, tp=tp)

def row(name, s):
    return (f"| {name} | {s['n']} | {s['acc']:.0%} | {s['bal']:.0%} | {s['mov']:.0%} ({s['tp']}/{s['tp'] + s['fn']}) "
            f"| {s['rest']:.0%} ({s['tn']}/{s['tn'] + s['fp']}) |")

train, test = recordings("train"), recordings("test")
P6 = "2026-11-19_112400_p6"          # excluded after the test was opened; shown apart
data = {n: windows(n) for n in train + test + [P6]}
stack = lambda names: (np.vstack([data[n][0] for n in names]), np.concatenate([data[n][1] for n in names]))
HEAD = "| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |\n|---|---|---|---|---|---|"

Ft, Lt = stack(train); model = MODELS[CHOSEN]().fit(Ft, Lt); ratio = float(np.exp(model.t))
out = ["# Results of the model", "",
       "Made with `python3 code/evaluate.py`.",
       f"Model: movement if the size of a window of 0.25 s (its mean absolute value) is above {ratio:.2f} times the rest level of the recording.",
       "Balanced accuracy is the mean of \"movement found\" and \"rest found\". We use it because there is about 4 times more rest than movement.", "",
       "## 1. Training (the model sees these windows)", "", HEAD]
for n in train: out.append(row(n[-2:], scores(data[n][1], model.predict(data[n][0]))))
s_train = scores(Lt, model.predict(Ft)); out += [row("all", s_train), ""]

out += ["## 2. Validation (leave one training recording out)", "",
        "Each row: the model is set with the other two recordings, then checked on this one. This is how we chose the model:", "",
        "| Model | " + " | ".join(n[-2:] for n in train) + " | all held-out windows |", "|---|" + "---|" * (len(train) + 1)]
for label, make in MODELS.items():
    per, yt, yp = validate(make, train, data)
    out.append(f"| {label}{' (chosen)' if label == CHOSEN else ''} | " + " | ".join(f"{balanced_accuracy_score(*per[n]):.0%}" for n in train) + f" | {balanced_accuracy_score(yt, yp):.0%} |")
per, yt, yp = validate(MODELS[CHOSEN], train, data); s_val = scores(yt, yp)
out += ["", "The chosen model in detail:", "", HEAD] + [row(n[-2:], scores(*per[n])) for n in train] + [row("all", s_val), ""]

Fe, Le = stack(test); pe = model.predict(Fe); s_test = scores(Le, pe)
out += ["## 3. Test (a recording the model never saw: p5)", "", HEAD, row("p5", s_test), "",
        "Note: p5 was first opened on 2026-11-23 with an earlier model (one fixed threshold of 2.93 counts, 87 % on p5). After that we changed the model to the one above. We chose the change with the validation table only, but we had already seen p5, so this is not a first look.", ""]

F6, L6 = data[P6]; p6 = model.predict(F6)
out += ["## 4. Recording p6, excluded after the test was opened", "", HEAD, row("p6", scores(L6, p6)), row("p5 + p6", scores(np.concatenate([Le, L6]), np.concatenate([pe, p6]))), "",
        "p6 was a test recording when we opened the test. After seeing it we took it out: its rest level is about 3.5 counts (0.6 to 2.1 in the others), and the board marked only 2 of about 12 visible contractions, so its labels are wrong: windows inside real contractions count as rest. With the earlier fixed threshold p6 scored 56 % and p5 + p6 scored 64 %. Taking a recording out after seeing the test makes the test score look better than a fair one.", ""]

out += ["## What this shows", "",
        f"- Training {s_train['bal']:.0%}, validation {s_val['bal']:.0%}, test {s_test['bal']:.0%} (balanced accuracy). The goal is more than 75 % on recordings never seen.",
        "- Measuring the size against the rest level of each recording is better than one fixed number of counts, because the rest level changes between recordings (0.6 to 3.5 counts).",
        "- Limits: one person, one session, labels from the KICK events of the board and not from a cue. The final test needs a cue video and new sessions with new electrodes.", ""]

# Figures
fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
for a, (t, s) in zip(ax, (("Training", s_train), ("Validation", s_val), ("Test (p5)", s_test))):
    m = np.array([[s["tn"], s["fp"]], [s["fn"], s["tp"]]]); a.imshow(m, cmap="Blues")
    for i in range(2):
        for j in range(2): a.text(j, i, m[i, j], ha="center", va="center", fontsize=14, color="white" if m[i, j] > m.max() / 2 else "black")
    a.set_xticks([0, 1]); a.set_xticklabels(["rest", "movement"]); a.set_yticks([0, 1]); a.set_yticklabels(["rest", "movement"])
    a.set_xlabel("model says"); a.set_ylabel("label"); a.set_title(f"{t}: balanced accuracy {s['bal']:.0%}")
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_confusion.png"), dpi=130)

fig, ax = plt.subplots(1, 2, figsize=(11, 3.6), sharey=True); bins = np.logspace(-0.5, 1.3, 40)
for a, (t, F, L) in zip(ax, (("Training", Ft, Lt), ("Test (p5)", Fe, Le))):
    r = np.exp(F[:, 2])
    a.hist(r[L == 0], bins, color="#7f7f7f", alpha=0.7, label="rest"); a.hist(r[L == 1], bins, color="#d95f02", alpha=0.7, label="movement")
    a.axvline(ratio, color="k", ls="--", label=f"threshold {ratio:.2f}"); a.set_xscale("log"); a.set_title(t)
    a.set_xlabel("size of the window / rest level"); a.legend()
ax[0].set_ylabel("windows"); fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_histogram.png"), dpi=130)

tl = test + [P6]
fig, ax = plt.subplots(len(tl), 1, figsize=(11, 2.8 * len(tl)))
for a, n in zip(np.atleast_1d(ax), tl):
    x, k = load(n); mav, _, rest = window_sizes(x); r = mav / rest; t = (np.arange(len(r)) + 0.5) * WIN / FS
    a.fill_between(t, 0, r.max() * (r > ratio), step="mid", color="#d95f02", alpha=0.25, lw=0, label="model says movement")
    a.plot(t, r, color="#1f4e79", lw=0.9, label="size / rest level"); a.axhline(ratio, color="k", ls="--", lw=0.8)
    a.plot(k / FS, np.full(len(k), r.max() * 1.03), "v", color="k", ms=5, label="KICK event of the board")
    a.set_title(f"Recording {n[-2:]}{' (excluded)' if n == P6 else ' (test)'}: every window of 0.25 s"); a.legend(fontsize=7, loc="upper right", ncol=3)
np.atleast_1d(ax)[-1].set_xlabel("seconds"); fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_test_timeline.png"), dpi=130)

out += ["## Figures", "", "- `figures/results_confusion.png`: right and wrong answers in training, validation and test.",
        "- `figures/results_histogram.png`: the size of the windows of each class against the rest level, and the threshold.",
        "- `figures/results_test_timeline.png`: what the model says along p5 and p6.", ""]
open(os.path.join(ROOT, "RESULTS.md"), "w").write("\n".join(out))
print("\n".join(out))
