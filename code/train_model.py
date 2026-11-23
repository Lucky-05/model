#!/usr/bin/env python3
"""First model: movement against rest. Uses ONLY the training recordings (set = train in
data/metadata.csv). The test recordings are not read here.

Needs numpy, scipy and scikit-learn.   Run from the repository root:  python3 code/train_model.py

Each example is a window of 0.25 s of the active channel, after the filters of PROTOCOL.md.
Features: log of the mean absolute value and log of the waveform length.
Labels (no cue video on 19 Nov): movement = windows that touch [KICK-0.25 s, KICK+0.25 s] of the
board; rest = windows more than 1.5 s away from every KICK; the rest of the signal has no label.
Score: balanced accuracy (the mean of "movement found" and "rest found"), because there is more
rest than movement. Validation: leave one recording out, so no recording is in both sides.
"""
import csv, json, os
import numpy as np
from scipy import signal
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import balanced_accuracy_score

ROOT = os.path.join(os.path.dirname(__file__), "..")
FS, WIN = 1000, 250

def recordings(which):
    with open(os.path.join(ROOT, "data", "metadata.csv")) as f:
        return [r["file_name"][:-len("_senal.csv")] for r in csv.DictReader(f) if r["set"] == which]

def load(name):
    with open(os.path.join(ROOT, "data", "raw", name + "_eventos.csv")) as f:
        ev = [(int(r["muestra"]), r["valor"]) for r in csv.DictReader(f) if r["tipo"] == "KICK"]
    ch = max("12", key=lambda c: sum(v == c for _, v in ev))          # the channel with the detections
    with open(os.path.join(ROOT, "data", "raw", name + "_senal.csv")) as f:
        x = np.array([float(r["canal" + ch]) for r in csv.DictReader(f)])
    return x, np.array([m for m, v in ev if v == ch])

def clean(x):
    b, a = signal.butter(4, [20, 450], btype="bandpass", fs=FS)
    y = signal.filtfilt(b, a, x)
    b, a = signal.iirnotch(60, 30, fs=FS)
    return signal.filtfilt(b, a, y)

def windows(name):
    x, k = load(name); y = clean(x); F, L = [], []
    for s in range(0, len(y) - WIN + 1, WIN):
        d = np.min(np.abs(k - (s + WIN / 2))) if len(k) else 1e9
        lab = 1 if d <= 250 + WIN / 2 else (0 if d > 1500 else None)
        if lab is None: continue
        w = y[s:s + WIN]
        F.append([np.log(np.mean(np.abs(w)) + 0.1), np.log(np.sum(np.abs(np.diff(w))) + 0.1)]); L.append(lab)
    return np.array(F), np.array(L)

class Threshold:
    """Movement if the first feature is above one number: the middle between the class medians."""
    def fit(self, F, L):
        self.t = (np.median(F[L == 1, 0]) + np.median(F[L == 0, 0])) / 2; return self
    def predict(self, F): return (F[:, 0] > self.t).astype(int)

MODELS = {"one threshold": lambda: Threshold(),
          "logistic regression": lambda: LogisticRegression(class_weight="balanced"),
          "decision tree, depth 2": lambda: DecisionTreeClassifier(max_depth=2, class_weight="balanced", random_state=0)}

if __name__ == "__main__":
    train = recordings("train"); data = {n: windows(n) for n in train}
    for n, (F, L) in data.items():
        print(f"{n}: {int(L.sum())} movement windows, {int((L == 0).sum())} rest windows")
    print("\nLeave one recording out (balanced accuracy):")
    print("| Model | " + " | ".join(n[-2:] for n in train) + " | all held-out windows |"); print("|---|" + "---|" * (len(train) + 1))
    for label, make in MODELS.items():
        cells, yt, yp = [], [], []
        for out in train:
            Ft = np.vstack([data[n][0] for n in train if n != out]); Lt = np.concatenate([data[n][1] for n in train if n != out])
            p = make().fit(Ft, Lt).predict(data[out][0])
            cells.append(f"{balanced_accuracy_score(data[out][1], p):.0%}"); yt.append(data[out][1]); yp.append(p)
        print(f"| {label} | " + " | ".join(cells) + f" | {balanced_accuracy_score(np.concatenate(yt), np.concatenate(yp)):.0%} |")
    F = np.vstack([data[n][0] for n in train]); L = np.concatenate([data[n][1] for n in train])
    m = LogisticRegression(class_weight="balanced").fit(F, L)
    t = Threshold().fit(F, L)
    out = {"model": "one threshold", "trained_on": train, "window_s": WIN / FS,
           "filters": "Butterworth 4 band-pass 20-450 Hz + notch 60 Hz Q30, zero phase",
           "rule": "movement if the mean absolute value of the window (counts of 10 bits) is above the threshold",
           "threshold_mav_counts": round(float(np.exp(t.t) - 0.1), 3),
           "windows": {"movement": int(L.sum()), "rest": int((L == 0).sum())},
           "alternative_logistic_regression": {
               "features": ["log(mean absolute value + 0.1)", "log(waveform length + 0.1)"],
               "coef": [round(float(c), 4) for c in m.coef_[0]], "intercept": round(float(m.intercept_[0]), 4),
               "rule": "movement if coef[0]*f0 + coef[1]*f1 + intercept > 0"}}
    json.dump(out, open(os.path.join(ROOT, "models", "model.json"), "w"), indent=1)
    print("\nSaved models/model.json: threshold", out["threshold_mav_counts"], "counts")
