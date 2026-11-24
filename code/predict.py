#!/usr/bin/env python3
"""Use the model on one recording: where does it see a contraction?

Needs numpy and scipy.   python3 code/predict.py <file_senal.csv> [canal1|canal2] [calibration_seconds]

Reads models/model.json. The rest level is the median size of the whole recording, or, if you
give calibration_seconds, of the first seconds of the recording (the person must be at rest then).
Contractions: neighbouring "movement" windows joined; pauses shorter than 1 s do not split one,
and a contraction lasts at least 0.5 s.
"""
import csv, json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from train_model import ROOT, FS, WIN, window_sizes

def predict(x, ratio, calibration_s=None):
    mav, _, rest = window_sizes(x)
    if calibration_s: rest = float(np.median(mav[:max(1, int(calibration_s * FS / WIN))]))
    return mav / rest > ratio, mav, rest

def contractions(on):
    runs, start, last = [], None, None
    for i, v in enumerate(list(on) + [False] * 5):
        if v:
            if start is None: start = i
            last = i
        elif start is not None and i - last >= 4:
            if last - start + 1 >= 2: runs.append((start * WIN / FS, (last + 1) * WIN / FS))
            start = None
    return runs

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    model = json.load(open(os.path.join(ROOT, "models", "model.json")))
    with open(sys.argv[1]) as f: rows = list(csv.DictReader(f))
    ch = sys.argv[2] if len(sys.argv) > 2 else max(("canal1", "canal2"), key=lambda c: np.std([float(r[c]) for r in rows]))
    cal = float(sys.argv[3]) if len(sys.argv) > 3 else None
    on, mav, rest = predict(np.array([float(r[ch]) for r in rows]), model["ratio"], cal)
    runs = contractions(on)
    print(f"{os.path.basename(sys.argv[1])}, {ch}: {len(rows) / FS:.1f} s, rest level {rest:.2f} counts, "
          f"movement if size > {model['ratio']} x rest = {model['ratio'] * rest:.2f} counts")
    print(f"{len(runs)} contractions, {100 * on.mean():.0f} % of the time in movement")
    for i, (a, b) in enumerate(runs, 1): print(f"  {i:2d}. {a:7.2f} s to {b:7.2f} s  ({b - a:.2f} s)")
