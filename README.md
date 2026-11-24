# Report 1: the data stage

Course: M6 Machine Learning and IoT apps. Project: tell a leg muscle contraction from rest with one muscle signal, to control a penalty-kick game.

> Draft. Lines marked TODO(team) need facts that only the team knows. Search for "TODO" before the tag `v1-report`.

## The team

| Member code | GitHub user | In charge of | AI tool |
|---|---|---|---|
| M01 | TODO | TODO | TODO |
| M02 | TODO | TODO | TODO |

We measure one person. In the data that person has the code P01. The folder names p1 ... p6 are the six recordings of that person, in order of time.

## The six parts

### 1. Data acquisition
6 recordings, 524 s, 1 person, 1 session, all on 2026-11-19. 38 contractions of about 3 s in the four recordings we use (p2: 3, p3: 11, p4: 10, p5: 14; `code/count_contractions.py`). Our goal was 50; p6 has about 12 more that we do not use. The board wrote 74 `KICK` events, up to 3 per contraction. Each channel of the board is one muscle: p1 has its signal on channel 1, p2 to p6 on channel 2. Our own amplifier with an analog band-pass filter, read by an ESP32 at 1000 samples per second. The signal is raw, not smoothed. TODO(team): electrodes, distance, the muscle of each channel.

**Evidence:** `data/raw/` (6 recordings, 4 files each), `data/metadata.csv` (6 rows).

### 2. Task
TODO(team): the movement and the posture. Two classes: movement and rest.

### 3. Trial and cue timing
On 19 Nov there was no cue video and no fixed timing: the person contracted when the game asked for a kick. The only time marks are the `KICK` events that the board wrote when its threshold detector fired. In p4 the contractions last about 3 s and repeat about every 8.6 s. TODO(team): the cue video and its seconds for the next recordings.

**Evidence:** `figures/one_recording_marked.png`, `data/raw/*_eventos.csv`.

### 4. Sessions
1 person, 1 session (S01): the six recordings are from one day, within 76 minutes, with the same electrode placement. This is less than the plan needs. Next: at least 3 more sessions on other days, each with new electrodes, the 1.65 V offset and a cue video.

### 5. Cleaning
Filters: band-pass Butterworth of order 4 from 20 to 450 Hz, then a notch at 60 Hz, both zero phase. Limits and sources in `PROTOCOL.md`.
Rule to reject, written before any score: a sample at a limit of the converter (0 or 1023), or more than 1 % of samples missing.
Result: 74 of 74 windows rejected, all for samples at 0. The amplifier had no offset on 19 Nov, so the lower half of the signal is cut in every recording. No sample reached 1023 and no recording has more than 0.7 % missing. Our choice: for this first version we keep the recordings and use a changed rule (the lower limit does not reject, because the signal rested there; the upper limit and gaps still reject: 0 of 74 rejected). For the next sessions we have added a 1.65 V offset to the circuit and changed the ESP32 range to 0-3.1 V, and the rule as written applies again.

**Evidence:** `QUALITY-REPORT.md`, `code/check_quality.py`.

### 6. Fair split
By time: p2, p3 and p4 train (138 movement windows, 531 rest windows of 0.25 s). p5 tests. p5 and p6 were both test recordings when we opened the test, once, on 2026-11-23 (`RESULTS.md`). After that we took p6 out, because its rest level and its labels are abnormal; `RESULTS.md` shows the score with and without it. p1 is not used for the model because it is the other channel (another muscle); we decided this after a first validation inside the training set, never with the test set. No recording is in both sets, and we do not shuffle windows of one recording between them. Limit: the six recordings share one electrode placement, so this split does not test "new electrodes". That test needs the new sessions.

**Evidence:** the column `set` of `data/metadata.csv`.

## What comes next
`DECISIONS.md` (features, model, route) and one file per member in `rationale/`. The model is in `models/model.json`, made by `code/train_model.py`: "movement if the size of a window of 0.25 s is above 2.02 times the rest level of the recording". All the results are in `RESULTS.md`:

| Stage | Recordings | Balanced accuracy |
|---|---|---|
| Training | p2, p3, p4 | 93 % |
| Validation, leaving one recording out | p2, p3, p4 | 91 % |
| Test | p5 | 91 % |

Limits, said plainly: one session, labels from the threshold detector of the board and not from a cue, p6 taken out after we saw the test, and the model changed once after the test was opened (chosen with validation only). The final score needs new sessions.

## How to repeat
`PROTOCOL.md`. Code: `python3 code/check_quality.py` (standard library) and `pip install -r requirements.txt`, then:
- `python3 code/check_quality.py` the quality table (standard library only)
- `python3 code/count_contractions.py` the contractions in each recording
- `python3 code/make_figures.py` the two figures of the data
- `python3 code/train_model.py` compares the models in validation and saves `models/model.json`
- `python3 code/evaluate.py` training, validation and test: `RESULTS.md` and `figures/results_*.png`
- `python3 code/predict.py data/raw/<file>_senal.csv` uses the model on one recording and lists its contractions
