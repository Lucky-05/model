# Decisions about what comes next

We chose with the training recordings only (session S02, contracciones1 to 4). The test recordings were opened after these choices (`RESULTS.md`).
The choices below were proposed by our AI tool from the numbers of `code/train_model.py`. TODO(team): rewrite each "Reason" in your own words and add what you do not understand yet.

## 7. Features
**Chose.** One number for each window of 0.25 s, after the filters: the mean absolute value of the window divided by the rest level of the recording (the median of all its windows). We also computed the waveform length and do not use it.
**Reason.** The size in counts depends on the day: the rest level went from 0.4 to 3.5 counts between recordings, and the range of our converter changed from 1.1 V to 3.1 V between the two sessions. Dividing by the rest level removes both. In `figures/two_features.png` the waveform length lies on one line with the size, so it repeats it.
**Not understood yet.** TODO(team). Open questions from the data: the signal is partly cut at the bottom, does that change which features are useful? In live use the rest level must come from a calibration at rest; how long must it be?
**Source.** Hudgins, Parker and Scott, "A new strategy for multifunction myoelectric control", IEEE Trans. Biomed. Eng., 1993. TODO(team): check it.

## 8. Model
**Chose.** One threshold on that feature: "movement if the size of the window is above 2.44 times the rest level" (`models/model.json`).

| Option | Balanced accuracy, leaving one training recording out |
|---|---|
| Threshold on the size, in counts | 92 % |
| Threshold on the size against rest (chosen) | 91 % |
| Logistic regression, in counts | 94 % |
| Logistic regression, against rest | 92 % |
| Decision tree of depth 2, in counts | 94 % |
| Decision tree of depth 2, against rest | 93 % |

**Reason.** The models in counts score a little higher inside one session, but they depend on the scale of the converter, which changed between our sessions, so they cannot be carried to another day. Among the three models against rest the difference is 2 points, less than the change from one recording to the next, so we keep the simplest: one number.
**Warning.** Our labels come from the threshold detector of the board, so a threshold model partly repeats its teacher. With a cue video the labels will come from the cue, and we will compare the options again.
**Not understood yet.** TODO(team)

## 9. Route
**Chose.** The model runs in our Python program on the computer. The ESP32 sends the signal over USB; the program already saves each session with its metadata (person code, start, end, sampling rate, thresholds, events) in Supabase and in local CSV files. We add the answer of the model to that record.
**Reason.** It needs the least new work and the record in the cloud already exists. Later the threshold is one number, so it can move to the ESP32.
**Proof.** TODO(team): a screenshot of Supabase with one saved session.
**Not understood yet.** TODO(team)
