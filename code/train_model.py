#!/usr/bin/env python3
"""Train the model: movement against rest. Uses ONLY the training recordings (set = train in
data/metadata.csv). The test recordings are not read here.

Needs numpy, scipy and scikit-learn.   Run from the repository root:  python3 code/train_model.py

Each example is a window of 0.25 s of the active channel, after the filters of PROTOCOL.md.
Features of a window:
  0  log of the mean absolute value (MAV), in counts
  1  log of the waveform length
  2  log of (MAV / rest level), where the rest level is the median MAV of the whole recording.
  3  log of (waveform length / its median in the recording)
     The person rests more than half of the time, so the median is the size of the signal at rest.
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

def window_sizes(x):
    """MAV and waveform length of every 0.25 s window of a raw signal, and its rest level."""
    y = clean(x); nw = len(y) // WIN; w = y[:nw * WIN].reshape(nw, WIN)
    mav = np.abs(w).mean(axis=1); wl = np.abs(np.diff(w, axis=1)).sum(axis=1)
    return mav, wl, float(np.median(mav)), float(np.median(wl))

def windows(name):
    """Features and labels of the labelled windows of one recording."""
    x, k = load(name); mav, wl, rest, rest_wl = window_sizes(x)
    mid = (np.arange(len(mav)) + 0.5) * WIN
    d = np.array([np.min(np.abs(k - c)) for c in mid]) if len(k) else np.full(len(mav), 1e9)
    lab = np.where(d <= 250 + WIN / 2, 1, np.where(d > 1500, 0, -1)); m = lab >= 0
    return np.c_[np.log(mav + 0.1), np.log(wl + 0.1), np.log(mav / rest), np.log(wl / rest_wl)][m], lab[m]

class Threshold:
    """Movement if one feature is above one number: the middle between the class medians."""
    def __init__(self, col): self.col = col
    def fit(self, F, L):
        self.t = (np.median(F[L == 1, self.col]) + np.median(F[L == 0, self.col])) / 2; return self
    def predict(self, F): return (F[:, self.col] > self.t).astype(int)

class Cols:
    """A scikit-learn model that sees only some of the features."""
    def __init__(self, m, cols): self.m, self.cols = m, cols
    def fit(self, F, L): self.m.fit(F[:, self.cols], L); return self
    def predict(self, F): return self.m.predict(F[:, self.cols])

def short(name): return name.split("_")[-1]

MODELS = {"threshold on the size (counts)": lambda: Threshold(0),
          "threshold on the size against rest": lambda: Threshold(2),
          "logistic regression (size, waveform length, in counts)": lambda: Cols(LogisticRegression(class_weight="balanced"), [0, 1]),
          "logistic regression (size, waveform length, against rest)": lambda: Cols(LogisticRegression(class_weight="balanced"), [2, 3]),
          "decision tree, depth 2 (size, waveform length, in counts)": lambda: Cols(DecisionTreeClassifier(max_depth=2, class_weight="balanced", random_state=0), [0, 1]),
          "decision tree, depth 2 (size, waveform length, against rest)": lambda: Cols(DecisionTreeClassifier(max_depth=2, class_weight="balanced", random_state=0), [2, 3])}
CHOSEN = "threshold on the size against rest"      # the best in validation; see the table this script prints

def validate(make, train, data):
    per, yt, yp = {}, [], []
    for out in train:
        F = np.vstack([data[n][0] for n in train if n != out]); L = np.concatenate([data[n][1] for n in train if n != out])
        p = make().fit(F, L).predict(data[out][0]); per[out] = (data[out][1], p); yt.append(data[out][1]); yp.append(p)
    return per, np.concatenate(yt), np.concatenate(yp)

if __name__ == "__main__":
    train = recordings("train"); data = {n: windows(n) for n in train}
    for n, (F, L) in data.items():
        print(f"{n}: {int(L.sum())} movement windows, {int((L == 0).sum())} rest windows")
    print("\nLeave one recording out (balanced accuracy):")
    print("| Model | " + " | ".join(short(n) for n in train) + " | all held-out windows |"); print("|---|" + "---|" * (len(train) + 1))
    for label, make in MODELS.items():
        per, yt, yp = validate(make, train, data)
        print(f"| {label} | " + " | ".join(f"{balanced_accuracy_score(*per[n]):.0%}" for n in train) + f" | {balanced_accuracy_score(yt, yp):.0%} |")
    F = np.vstack([data[n][0] for n in train]); L = np.concatenate([data[n][1] for n in train])
    m = MODELS[CHOSEN]().fit(F, L)
    out = {"model": CHOSEN, "trained_on": train, "window_s": WIN / FS,
           "filters": "Butterworth 4 band-pass 20-450 Hz + notch 60 Hz Q30, zero phase",
           "rest_level": "median of the mean absolute value of all the 0.25 s windows of the recording (or of a calibration at rest)",
           "rule": "movement if the mean absolute value of the window is above ratio x rest level",
           "ratio": round(float(np.exp(m.t)), 3),
           "windows": {"movement": int(L.sum()), "rest": int((L == 0).sum())}}
    json.dump(out, open(os.path.join(ROOT, "models", "model.json"), "w"), indent=1)
    print(f"\nSaved models/model.json: movement if size > {out['ratio']} x rest level")
