# Results of the model

Made with `python3 code/evaluate.py`.
Model: movement if the size of a window of 0.25 s (its mean absolute value) is above 2.02 times the rest level of the recording.
Balanced accuracy is the mean of "movement found" and "rest found". We use it because there is about 4 times more rest than movement.

## 1. Training (the model sees these windows)

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p2 | 86 | 87% | 93% | 100% (6/6) | 86% (69/80) |
| p3 | 332 | 97% | 92% | 85% (61/72) | 100% (260/260) |
| p4 | 251 | 96% | 95% | 92% (55/60) | 97% (186/191) |
| all | 669 | 95% | 93% | 88% (122/138) | 97% (515/531) |

## 2. Validation (leave one training recording out)

Each row: the model is set with the other two recordings, then checked on this one. This is how we chose the model:

| Model | p2 | p3 | p4 | all held-out windows |
|---|---|---|---|---|
| threshold on the size (counts) | 94% | 82% | 90% | 86% |
| threshold on the size against rest (chosen) | 93% | 88% | 95% | 91% |
| logistic regression (size, waveform length) | 94% | 74% | 92% | 83% |
| decision tree, depth 2 (size, waveform length) | 94% | 57% | 93% | 75% |

The chosen model in detail:

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p2 | 86 | 87% | 93% | 100% (6/6) | 86% (69/80) |
| p3 | 332 | 95% | 88% | 75% (54/72) | 100% (260/260) |
| p4 | 251 | 95% | 95% | 95% (57/60) | 95% (182/191) |
| all | 669 | 94% | 91% | 85% (117/138) | 96% (511/531) |

## 3. Test (a recording the model never saw: p5)

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p5 | 357 | 94% | 91% | 86% (59/69) | 96% (276/288) |

Note: p5 was first opened on 2026-11-23 with an earlier model (one fixed threshold of 2.93 counts, 87 % on p5). After that we changed the model to the one above. We chose the change with the validation table only, but we had already seen p5, so this is not a first look.

## 4. Recording p6, excluded after the test was opened

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p6 | 390 | 89% | 78% | 67% (4/6) | 89% (342/384) |
| p5 + p6 | 747 | 91% | 88% | 84% (63/75) | 92% (618/672) |

p6 was a test recording when we opened the test. After seeing it we took it out: its rest level is about 3.5 counts (0.6 to 2.1 in the others), and the board marked only 2 of about 12 visible contractions, so its labels are wrong: windows inside real contractions count as rest. With the earlier fixed threshold p6 scored 56 % and p5 + p6 scored 64 %. Taking a recording out after seeing the test makes the test score look better than a fair one.

## What this shows

- Training 93%, validation 91%, test 91% (balanced accuracy). The goal is more than 75 % on recordings never seen.
- Measuring the size against the rest level of each recording is better than one fixed number of counts, because the rest level changes between recordings (0.6 to 3.5 counts).
- Limits: one person, one session, labels from the KICK events of the board and not from a cue. The final test needs a cue video and new sessions with new electrodes.

## Figures

- `figures/results_confusion.png`: right and wrong answers in training, validation and test.
- `figures/results_histogram.png`: the size of the windows of each class against the rest level, and the threshold.
- `figures/results_test_timeline.png`: what the model says along p5 and p6.
