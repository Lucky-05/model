#!/usr/bin/env python3
"""Count the contractions in each recording, without using the KICK events of the board.

Needs numpy and scipy.   Run from the repository root:  python3 code/count_contractions.py
A contraction = the mean absolute value of windows of 0.25 s stays above 2.5 times the median of the
recording (its rest level) for at least 0.75 s. Pauses shorter than 1 s do not split a contraction.
"""
import csv, glob, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from train_model import ROOT, FS, WIN, load, clean

def contractions(name):
    x, k = load(name); y = clean(x); nw = len(y) // WIN
    mav = np.abs(y[:nw * WIN]).reshape(nw, WIN).mean(axis=1)
    rest = np.median(mav); on = mav > 2.5 * rest
    runs, start, gap = [], None, 0
    for i, v in enumerate(list(on) + [False] * 5):
        if v:
            if start is None: start = i
            gap = 0; last = i
        elif start is not None:
            gap += 1
            if gap >= 4:                                   # 1 s of rest closes the contraction
                if last - start + 1 >= 3: runs.append((start * WIN / FS, (last + 1) * WIN / FS))
                start = None
    return runs, rest, len(k)

if __name__ == "__main__":
    print("| Recording | Seconds | Rest level (counts) | Contractions | Mean length (s) | KICK events of the board |"); print("|---|---|---|---|---|---|")
    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "*_senal.csv"))):
        n = os.path.basename(p)[:-len("_senal.csv")]; r, rest, k = contractions(n); total += len(r)
        with open(p) as f: secs = (sum(1 for _ in f) - 1) / FS
        ml = np.mean([b - a for a, b in r]) if r else 0
        print(f"| {n.split('_')[-1]} | {secs:.0f} | {rest:.2f} | {len(r)} | {ml:.1f} | {k} |")
    print(f"\nTotal: {total} contractions.")
