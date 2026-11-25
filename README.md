# Report 1: the data stage

Course: M6 Machine Learning and IoT apps. Project: tell a contraction of the hamstrings from rest with one muscle signal, to control a penalty-kick game.

> Draft. Lines marked TODO(team) need facts that only the team knows. Search for "TODO" before the tag `v1-report`.

## The team

| Member code | GitHub user | In charge of | AI tool |
|---|---|---|---|
| M01 | @Lucky-05 | recordings, code, quality check and first model | Claude Code |
| M02 | TODO(team) | TODO(team) | TODO(team) |

We measure one person. In the data that person has the code P01. The folder names p1 ... p6 are the six recordings of that person, in order of time.

## The six parts

### 1. Data acquisition
12 recordings, 991 s, 1 person, 2 sessions (19 Nov and 24 Nov 2026). Our own amplifier with an analog band-pass filter, read by an ESP32 at 1000 samples per second. The signal is raw, not smoothed. Channel 1 is the quadriceps and channel 2 the hamstrings; our movement is the one of channel 2.

| Session | Date | Recordings we use | Contractions (`code/count_contractions.py`) |
|---|---|---|---|
| S01 | 2026-11-19 | p2, p3, p4, p5 | 3 + 11 + 10 + 14 = 38 |
| S02 | 2026-11-24 | contracciones1 to contracciones5 | 10 + 1 + 15 + 15 + 10 = 51 |

Not used: p1 (signal on the other channel), p6 (abnormal, see `RESULTS.md`), prueba2canales (a check of both channels, without labels). TODO(team): electrode type, distance between them, skin preparation, gain. TODO(team): confirm that S02 is the same person as S01.

**Evidence:** `data/raw/` (12 recordings, 4 files each), `data/metadata.csv` (12 rows).

### 2. Task
The person contracts the hamstrings of one leg, holds the contraction about 2.5 to 3.5 s, and relaxes. Two classes: movement and rest. TODO(team): the side, the posture and the exact movement of the leg.

### 3. Trial and cue timing
There was no cue video. In S01 the person contracted when the game asked for a kick. In S02 the person kept a rhythm alone: about 2.5 s of contraction every 7 s (measured from the signal), 10 or 15 contractions per recording. The only time marks are the `KICK` events that the board wrote when its threshold detector fired, 1 to 3 per contraction. TODO(team): the cue video and its seconds for the next recordings.

**Evidence:** `figures/one_recording_marked.png`, `figures/results_test_timeline.png`, `data/raw/*_eventos.csv`.

### 4. Sessions
1 person, 2 sessions on 2 days, 5 days apart, with electrodes placed again. S01: 6 recordings within 76 minutes. S02: 6 recordings within 90 minutes. Between the sessions the circuit changed: an offset was added, the amplifier moved to a PCB, and the ESP32 range went from 0-1.1 V to 0-3.1 V. In S02 channel 1 was dead in contracciones1 to 5 because one ESP32 pin was damaged; the board was replaced before prueba2canales. TODO(team): one photo of the electrodes per session.

### 5. Cleaning
Filters: band-pass Butterworth of order 4 from 20 to 450 Hz, then a notch at 60 Hz, both zero phase. Limits and sources in `PROTOCOL.md`.
Rule to reject, written before any score: a sample at a limit of the converter (0 or 1023), or more than 1 % of samples missing.
Result: S01, 74 of 74 windows rejected, all for samples at 0, because the amplifier had no offset and the lower half of the signal was cut. S02, 0 of 67 windows rejected: no sample at 0 or at 1023. For S01 we use a changed rule (the lower limit does not reject), and we say so. In S02 the signal still rests low (about 0.1 V, not 1.65 V), so part of the lower half is still cut although no sample reaches 0.

**Evidence:** `QUALITY-REPORT.md`, `code/check_quality.py`.

### 6. Fair split
Training: S02, contracciones1 to contracciones4 (165 movement windows and 737 rest windows of 0.25 s).
Test A, same session: contracciones5, never used to train.
Test B, another session: S01 (p2 to p5), another day and another electrode placement. This is the test the project asks for.
No recording is in both sets, and we do not shuffle windows of one recording between them. Limit, said plainly: the recordings of S01 are not new to us. An earlier model was built and tested on them on 2026-11-23, and the idea of measuring the size against the rest level came from them. The model of this version was trained without them.

**Evidence:** the columns `session` and `set` of `data/metadata.csv`.

## What comes next
`DECISIONS.md` (features, model, route) and one file per member in `rationale/`. The model is in `models/model.json`, made by `code/train_model.py`: "movement if the size of a window of 0.25 s is above 2.44 times the rest level of the recording". All the results are in `RESULTS.md`:

| Stage | Recordings | Balanced accuracy |
|---|---|---|
| Training | S02: contracciones1 to 4 | 92 % |
| Validation, leaving one recording out | S02: contracciones1 to 4 | 91 % |
| Test, same session | S02: contracciones5 | 95 % |
| Test, another session | S01: p2 to p5 | 89 % |

Limits: one person, two sessions, labels from the threshold detector of the board and not from a cue. The next step is a cue video and a third session that nobody has looked at.

## How to repeat
`PROTOCOL.md`. Code: `python3 code/check_quality.py` (standard library) and `pip install -r requirements.txt`, then:
- `python3 code/check_quality.py` the quality table (standard library only)
- `python3 code/count_contractions.py` the contractions in each recording
- `python3 code/make_figures.py` the two figures of the data
- `python3 code/train_model.py` compares the models in validation and saves `models/model.json`
- `python3 code/evaluate.py` training, validation and test: `RESULTS.md` and `figures/results_*.png`
- `python3 code/predict.py data/raw/<file>_senal.csv` uses the model on one recording and lists its contractions
