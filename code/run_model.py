#!/usr/bin/env python3
"""Run the model on one measurement and save the record, with its metadata, locally and in the cloud.

Needs numpy and scipy.

  From a file:   python3 code/run_model.py data/raw/<name>_senal.csv --person P01 --session S02
  Live:          python3 code/run_model.py --live 30 --person P01 --session S03
                 (reads 30 s from our Python bridge at http://127.0.0.1:5010/flujo; the bridge must run)
  Options:       --channel canal2      the channel of the muscle (default canal2, hamstrings)
                 --calibration 5       seconds of rest at the start used as the rest level
                                       (without it: the median of the whole measurement)
                 --upload              also save the record in Supabase

One record = date and time, person code, session, source, channel, sampling rate, seconds, the model
and its number, the rest level, and every contraction the model found (start, end, size).
It is written to records/<date>_<person>_<session>.json. With --upload it also goes to our Supabase
project: one row in `sesiones` and rows in `eventos` (tipo MODELO and CONTRACCION). The address and
the key of the project are read from ~/.config/emg-penales/supabase.env and are never in this repository.
"""
import argparse, csv, json, os, sys, time, urllib.request
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from train_model import ROOT, FS, WIN
from predict import predict, contractions

BRIDGE = "http://127.0.0.1:5010/flujo"
CONFIG = os.path.expanduser("~/.config/emg-penales/supabase.env")

def read_file(path, channel):
    with open(path) as f:
        return np.array([float(r[channel]) for r in csv.DictReader(f)])

def read_live(seconds, channel):
    """Samples of one channel from the bridge (Server-Sent Events: 'data: a,b;a,b;...')."""
    col = int(channel[-1]) - 1; x = []
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(BRIDGE, timeout=5) as r:
        end = time.time() + seconds
        while time.time() < end:
            line = r.readline().decode(errors="replace").strip()
            if line.startswith("data: ") and line[6:7].isdigit():
                for pair in line[6:].split(";"):
                    try: x.append(float(pair.split(",")[col]))
                    except (ValueError, IndexError): pass
    return np.array(x)

def upload(record):
    cfg = {}
    with open(CONFIG) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1); cfg[k] = v
    def ask(method, route, body, back=False):
        req = urllib.request.Request(cfg["SUPABASE_URL"] + "/rest/v1/" + route, data=json.dumps(body).encode(), method=method,
                                     headers={"apikey": cfg["SUPABASE_KEY"], "Authorization": "Bearer " + cfg["SUPABASE_KEY"],
                                              "Content-Type": "application/json", "Prefer": "return=representation" if back else "return=minimal"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read() or b"null") if back else None
    sid = ask("POST", "sesiones", {"paciente": record["person"]}, back=True)[0]["id"]
    head = {k: v for k, v in record.items() if k != "contractions"}
    rows = [{"sesion_id": sid, "muestra": 0, "tipo": "MODELO", "valor": json.dumps(head, separators=(",", ":"))}]
    rows += [{"sesion_id": sid, "muestra": int(c["start_s"] * FS), "tipo": "CONTRACCION",
              "valor": f"{c['start_s']},{c['end_s']},{c['peak_size_over_rest']}"} for c in record["contractions"]]
    ask("POST", "eventos", rows)
    ask("PATCH", "sesiones?id=eq." + str(sid), {"fin": record["datetime"]})
    return sid

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Run the model on one measurement and save the record.")
    ap.add_argument("file", nargs="?"); ap.add_argument("--live", type=float, metavar="SECONDS")
    ap.add_argument("--person", required=True); ap.add_argument("--session", required=True)
    ap.add_argument("--channel", default="canal2", choices=["canal1", "canal2"])
    ap.add_argument("--calibration", type=float); ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()
    if bool(a.file) == bool(a.live): ap.error("give a file or --live SECONDS")
    model = json.load(open(os.path.join(ROOT, "models", "model.json")))
    x = read_live(a.live, a.channel) if a.live else read_file(a.file, a.channel)
    if len(x) < 4 * WIN: sys.exit(f"only {len(x)} samples: nothing to classify (is the bridge running and the board connected?)")
    on, mav, rest = predict(x, model["ratio"], a.calibration)
    runs = contractions(on)
    record = {"datetime": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "person": a.person, "session": a.session,
              "source": "live" if a.live else os.path.basename(a.file), "channel": a.channel, "fs_hz": FS,
              "seconds": round(len(x) / FS, 1), "model": model["model"], "ratio": model["ratio"], "window_s": model["window_s"],
              "trained_on": [n.split("_")[-1] for n in model["trained_on"]],
              "rest_level_counts": round(rest, 3), "rest_level_from": f"first {a.calibration} s" if a.calibration else "median of the measurement",
              "contractions_found": len(runs), "percent_of_time_in_movement": round(100 * float(on.mean()), 1),
              "contractions": [{"start_s": s, "end_s": e, "peak_size_over_rest": round(float(mav[int(s * FS / WIN):int(e * FS / WIN)].max() / rest), 1)} for s, e in runs]}
    path = os.path.join(ROOT, "records", f"{time.strftime('%Y-%m-%d_%H%M%S')}_{a.person}_{a.session}.json")
    json.dump(record, open(path, "w"), indent=1)
    print(f"{record['source']}, {a.channel}: {record['seconds']} s, rest level {rest:.2f} counts")
    print(f"{len(runs)} contractions, {record['percent_of_time_in_movement']} % of the time in movement")
    for i, c in enumerate(record["contractions"], 1): print(f"  {i:2d}. {c['start_s']:7.2f} s to {c['end_s']:7.2f} s   size {c['peak_size_over_rest']} x rest")
    print("saved:", os.path.relpath(path, ROOT))
    if a.upload:
        try: print("saved in Supabase: sesiones.id =", upload(record))
        except Exception as e: print("could NOT save in Supabase:", e)
