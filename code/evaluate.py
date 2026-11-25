#!/usr/bin/env python3
"""Train, validate and test the model, and draw the results.

Needs numpy, scipy, scikit-learn and matplotlib.   Run from the repository root:  python3 code/evaluate.py
WARNING: this script READS THE TEST RECORDINGS (set = test). Writes RESULTS.md and figures/results_*.png.

Training: session S02 (24 Nov), recordings with set = train.
Test A, same session: the recording of S02 with set = test (same electrodes, never used to train).
Test B, other session: the recordings of S01 (19 Nov) with set = test. Other day, other electrode
placement, other ESP32 input range (1.1 V against 3.1 V). This is the test that the project asks for.
"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
sys.path.insert(0, os.path.dirname(__file__))
from train_model import ROOT, FS, WIN, MODELS, CHOSEN, load, window_sizes, windows, validate, short

def scores(L, p):
    tn, fp, fn, tp = confusion_matrix(L, p, labels=[0, 1]).ravel()
    return dict(n=len(L), acc=(tp + tn) / len(L), bal=balanced_accuracy_score(L, p),
                mov=tp / (tp + fn) if tp + fn else float("nan"), rest=tn / (tn + fp), tn=tn, fp=fp, fn=fn, tp=tp)

def row(name, s):
    return (f"| {name} | {s['n']} | {s['acc']:.0%} | {s['bal']:.0%} | {s['mov']:.0%} ({s['tp']}/{s['tp'] + s['fn']}) "
            f"| {s['rest']:.0%} ({s['tn']}/{s['tn'] + s['fp']}) |")

with open(os.path.join(ROOT, "data", "metadata.csv")) as f:
    meta = [(r["file_name"][:-len("_senal.csv")], r["session"], r["set"]) for r in csv.DictReader(f)]
train = [n for n, s, st in meta if st == "train"]
test_a = [n for n, s, st in meta if st == "test" and s == "S02"]
test_b = [n for n, s, st in meta if st == "test" and s == "S01"]
data = {n: windows(n) for n in train + test_a + test_b}
stack = lambda names: (np.vstack([data[n][0] for n in names]), np.concatenate([data[n][1] for n in names]))
HEAD = "| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |\n|---|---|---|---|---|---|"

Ft, Lt = stack(train); model = MODELS[CHOSEN]().fit(Ft, Lt); ratio = float(np.exp(model.t))
out = ["# Results of the model", "",
       "Made with `python3 code/evaluate.py`.",
       f"Model: movement if the size of a window of 0.25 s (its mean absolute value) is above {ratio:.2f} times the rest level of the recording.",
       "Balanced accuracy is the mean of \"movement found\" and \"rest found\". We use it because there is about 4 times more rest than movement.", "",
       "## 1. Training (session S02, 24 Nov; the model sees these windows)", "", HEAD]
out += [row(short(n), scores(data[n][1], model.predict(data[n][0]))) for n in train]
s_train = scores(Lt, model.predict(Ft)); out += [row("all", s_train), ""]

out += ["## 2. Validation (leave one training recording out)", "",
        "Each column: the model is set with the other training recordings, then checked on this one.", "",
        "| Model | " + " | ".join(short(n) for n in train) + " | all held-out windows |", "|---|" + "---|" * (len(train) + 1)]
for label, make in MODELS.items():
    per, yt, yp = validate(make, train, data)
    out.append(f"| {label}{' (chosen)' if label == CHOSEN else ''} | " + " | ".join(f"{balanced_accuracy_score(*per[n]):.0%}" for n in train) + f" | {balanced_accuracy_score(yt, yp):.0%} |")
per, yt, yp = validate(MODELS[CHOSEN], train, data); s_val = scores(yt, yp)
out += ["", "How we chose. The models \"in counts\" depend on the scale of the converter, and that scale changed between our sessions (0-1.1 V on 19 Nov, 0-3.1 V on 24 Nov), so they cannot be used on another session. Among the three models \"against rest\" the scores are 91 % to 93 %, a difference smaller than the change from one recording to the next. We keep the simplest one.", "",
        "The chosen model in detail:", "", HEAD] + [row(short(n), scores(*per[n])) for n in train] + [row("all", s_val), ""]

Fa, La = stack(test_a); pa = model.predict(Fa); s_a = scores(La, pa)
out += ["## 3. Test A: same session, a recording never used to train", "", HEAD] + [row(short(n), scores(data[n][1], model.predict(data[n][0]))) for n in test_a] + [""]

Fb, Lb = stack(test_b); pb = model.predict(Fb); s_b = scores(Lb, pb)
out += ["## 4. Test B: another session (S01, 19 Nov, other electrode placement)", "", HEAD]
out += [row(short(n), scores(data[n][1], model.predict(data[n][0]))) for n in test_b] + [row("all", s_b), "",
        "Note: these recordings are not new to us. An earlier model was built and tested on them (see the history of this repository), and that is where the idea of measuring the size against the rest level came from. The model above was trained without them, on S02 only.",
        "p1 (other muscle) and p6 (abnormal rest level and wrong labels, taken out on 2026-11-23 after we saw its score) are not used.", ""]

out += ["## What this shows", "",
        f"- Training {s_train['bal']:.0%}, validation {s_val['bal']:.0%}, test in the same session {s_a['bal']:.0%}, test in another session {s_b['bal']:.0%} (balanced accuracy). The goal is more than 75 % on sessions never seen.",
        "- The same number works on two days with different electrodes and a different converter range, because the size is measured against the rest level of each recording.",
        "- Limits: one person, two sessions, self-paced contractions. The labels come from the KICK events of the board, not from a cue video. The signal rests near the lower limit of the converter, so its lower half is cut.", ""]

# Figures
fig, ax = plt.subplots(1, 4, figsize=(14.5, 3.6))
for a, (t, s) in zip(ax, (("Training", s_train), ("Validation", s_val), ("Test, same session", s_a), ("Test, other session", s_b))):
    m = np.array([[s["tn"], s["fp"]], [s["fn"], s["tp"]]]); a.imshow(m, cmap="Blues")
    for i in range(2):
        for j in range(2): a.text(j, i, m[i, j], ha="center", va="center", fontsize=14, color="white" if m[i, j] > m.max() / 2 else "black")
    a.set_xticks([0, 1]); a.set_xticklabels(["rest", "movement"]); a.set_yticks([0, 1]); a.set_yticklabels(["rest", "movement"])
    a.set_xlabel("model says"); a.set_ylabel("label"); a.set_title(f"{t}: {s['bal']:.0%}", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_confusion.png"), dpi=130)

fig, ax = plt.subplots(1, 3, figsize=(14, 3.6), sharey=False); bins = np.logspace(-0.5, 1.7, 45)
for a, (t, F, L) in zip(ax, (("Training (S02)", Ft, Lt), ("Test, same session", Fa, La), ("Test, other session (S01)", Fb, Lb))):
    r = np.exp(F[:, 2])
    a.hist(r[L == 0], bins, color="#7f7f7f", alpha=0.7, label="rest"); a.hist(r[L == 1], bins, color="#d95f02", alpha=0.7, label="movement")
    a.axvline(ratio, color="k", ls="--", label=f"threshold {ratio:.2f}"); a.set_xscale("log"); a.set_title(t)
    a.set_xlabel("size of the window / rest level"); a.legend()
ax[0].set_ylabel("windows"); fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_histogram.png"), dpi=130)

tl = test_a + test_b[-1:]
fig, ax = plt.subplots(len(tl), 1, figsize=(11, 2.8 * len(tl)))
for a, n in zip(np.atleast_1d(ax), tl):
    x, k = load(n); mav, _, rest, _ = window_sizes(x); r = mav / rest; t = (np.arange(len(r)) + 0.5) * WIN / FS
    a.fill_between(t, 0, r.max() * (r > ratio), step="mid", color="#d95f02", alpha=0.25, lw=0, label="model says movement")
    a.plot(t, r, color="#1f4e79", lw=0.9, label="size / rest level"); a.axhline(ratio, color="k", ls="--", lw=0.8)
    a.plot(k / FS, np.full(len(k), r.max() * 1.03), "v", color="k", ms=5, label="KICK event of the board")
    a.set_title(f"Test recording {short(n)} ({'same session' if n in test_a else 'other session'}): every window of 0.25 s"); a.legend(fontsize=7, loc="upper right", ncol=3)
np.atleast_1d(ax)[-1].set_xlabel("seconds"); fig.tight_layout(); fig.savefig(os.path.join(ROOT, "figures", "results_test_timeline.png"), dpi=130)

out += ["## Figures", "", "- `figures/results_confusion.png`: right and wrong answers in training, validation and the two tests.",
        "- `figures/results_histogram.png`: the size of the windows of each class against the rest level, and the threshold.",
        "- `figures/results_test_timeline.png`: what the model says along one test recording of each session.", ""]
open(os.path.join(ROOT, "RESULTS.md"), "w").write("\n".join(out))
print("\n".join(out))
