# Decisions about what comes next

We chose with the training recordings only (p2, p3, p4). The test recordings (p5, p6) are still closed.
The choices below were proposed by our AI tool from the numbers of `code/train_model.py`. TODO(team): rewrite each "Reason" in your own words and add what you do not understand yet.

## 7. Features
**Chose.** One number for each window of 0.25 s, after the filters: the mean absolute value. We also computed the waveform length and do not use it for now.
**Reason.** In the training recordings the mean absolute value alone separates the classes: median 7.26 and 5.22 counts in movement against 1.85 and 0.71 at rest (p3, p4). In `figures/two_features.png` the two features lie on one line, so the second repeats the first.
**Not understood yet.** TODO(team). One open question from the data: our signal is cut at 0, does that change which features are useful?
**Source.** Hudgins, Parker and Scott, "A new strategy for multifunction myoelectric control", IEEE Trans. Biomed. Eng., 1993. TODO(team): check it.

## 8. Model
**Chose.** One threshold: "movement if the mean absolute value of the window is above 2.9 counts" (the exact number is in `models/model.json`).

| Option | p2 | p3 | p4 | all held-out windows |
|---|---|---|---|---|
| One threshold | 94 % | 82 % | 90 % | 86 % |
| Logistic regression (2 features) | 94 % | 74 % | 92 % | 83 % |
| Decision tree, depth 2 | 94 % | 57 % | 93 % | 75 % |

Balanced accuracy, leaving one training recording out each time.
**Reason.** The simplest model was also the best on recordings it did not see, and it keeps one number.
**Warning.** Our labels come from the threshold detector of the board, so a threshold model partly repeats its teacher. With a cue video the labels will come from the cue, and we will compare the three options again.
**Not understood yet.** TODO(team)

## 9. Route
**Chose.** The model runs in our Python program on the computer. The ESP32 sends the signal over USB; the program already saves each session with its metadata (person code, start, end, sampling rate, thresholds, events) in Supabase and in local CSV files. We add the answer of the model to that record.
**Reason.** It needs the least new work and the record in the cloud already exists. Later the threshold is one number, so it can move to the ESP32.
**Proof.** TODO(team): a screenshot of Supabase with one saved session.
**Not understood yet.** TODO(team)
