#!/usr/bin/env python3
"""Quality check of every recording in data/raw/. Standard library only.

Run from the repository root:   python3 code/check_quality.py
It prints the table that we paste in QUALITY-REPORT.md. It never changes a raw file.

Rule, fixed before any model score: a window is rejected if one of its samples sits at a limit
of the converter (0 or 1023), or if more than 1 % of the samples of the recording are missing.
A "window" here is 1 s around each contraction that the board detected (0.3 s before the KICK
event to 0.7 s after it), on the channel where it was detected.
"""
import csv, glob, json, os
from datetime import datetime

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
LOW, HIGH = 0.5, 1022.5          # counts of 10 bits; the board sends one decimal
BEFORE, AFTER = 300, 700         # samples (ms) around a KICK event

def pct(n, d): return 100.0 * n / d if d else 0.0

rows = []
for path in sorted(glob.glob(os.path.join(RAW, "*_senal.csv"))):
    base = path[:-len("_senal.csv")]
    ch = [[], []]
    with open(path) as f:
        for r in csv.DictReader(f):
            ch[0].append(float(r["canal1"])); ch[1].append(float(r["canal2"]))
    n = len(ch[0])
    meta = json.load(open(base + "_sesion.json"))
    fmt = "%Y-%m-%dT%H:%M:%S%z"
    wall = (datetime.strptime(meta["fin"], fmt) - datetime.strptime(meta["inicio"], fmt)).total_seconds()
    missing = max(0.0, 100 * (1 - n / (wall * meta["fs"]))) if wall else 0.0   # clock has 1 s steps
    kicks = [[], []]
    with open(base + "_eventos.csv") as f:
        for r in csv.DictReader(f):
            if r["tipo"] == "KICK": kicks[int(r["valor"]) - 1].append(int(r["muestra"]))
    out = {"file": os.path.basename(path), "n": n, "s": n / meta["fs"], "missing": missing}
    for c in (0, 1):
        x = ch[c]
        out[f"low{c+1}"] = pct(sum(v <= LOW for v in x), n)
        out[f"high{c+1}"] = pct(sum(v >= HIGH for v in x), n)
        out[f"max{c+1}"] = max(x)
        rej = 0
        for k in kicks[c]:
            w = x[max(0, k - BEFORE): k + AFTER]
            if any(v <= LOW or v >= HIGH for v in w): rej += 1
        out[f"k{c+1}"] = len(kicks[c]); out[f"rej{c+1}"] = rej
    rows.append(out)

print("| File | Seconds | Missing % | Ch1 at 0 % | Ch1 at 1023 % | Ch1 max | Ch1 windows (rejected) | Ch2 at 0 % | Ch2 at 1023 % | Ch2 max | Ch2 windows (rejected) |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for o in rows:
    print(f"| {o['file']} | {o['s']:.1f} | {o['missing']:.1f} | {o['low1']:.1f} | {o['high1']:.2f} | {o['max1']:.0f} | {o['k1']} ({o['rej1']}) "
          f"| {o['low2']:.1f} | {o['high2']:.2f} | {o['max2']:.0f} | {o['k2']} ({o['rej2']}) |")
t = sum(o["k1"] + o["k2"] for o in rows); r = sum(o["rej1"] + o["rej2"] for o in rows)
print(f"\nTotal: {len(rows)} recordings, {sum(o['s'] for o in rows):.0f} s, {t} detected windows, {r} rejected, {t - r} kept.")
