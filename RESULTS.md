# Results of the first model

Made with `python3 code/evaluate.py`. Model: one threshold on the mean absolute value of a window of 0.25 s.
Balanced accuracy is the mean of "movement found" and "rest found". We use it because there is about 4 times more rest than movement.

## 1. Training (the model sees these windows)

Threshold: 2.93 counts.

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p2 | 86 | 90% | 94% | 100% (6/6) | 89% (71/80) |
| p3 | 332 | 98% | 98% | 97% (70/72) | 98% (255/260) |
| p4 | 251 | 96% | 93% | 87% (52/60) | 99% (189/191) |
| all | 669 | 96% | 95% | 93% (128/138) | 97% (515/531) |

## 2. Validation (leave one training recording out)

Each row: the threshold is set with the other two recordings, then checked on this one.

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p2 | 86 | 90% | 94% | 100% (6/6) | 89% (71/80) |
| p3 | 332 | 73% | 82% | 100% (72/72) | 65% (169/260) |
| p4 | 251 | 95% | 90% | 80% (48/60) | 99% (190/191) |
| all | 669 | 83% | 86% | 91% (126/138) | 81% (430/531) |

## 3. Test (a recording the model never saw: p5)

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p5 | 357 | 93% | 87% | 78% (54/69) | 97% (278/288) |
| all | 357 | 93% | 87% | 78% (54/69) | 97% (278/288) |

## 4. Recording p6, excluded after the test was opened

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p6 | 390 | 13% | 56% | 100% (6/6) | 12% (45/384) |
| p5 + p6 | 747 | 51% | 64% | 80% (60/75) | 48% (323/672) |

p6 was a test recording when we opened the test on 2026-11-23. After seeing it we took it out: its rest level is about 3.5 counts (0.6 to 2.1 in the others), and the board marked only 2 of about 12 visible contractions, so its labels are wrong. We show its score here so that nothing is hidden. Taking a recording out after seeing the test makes the test score look better than a fair one.

## What this shows

- Training 95%, validation 86%, test 87% (balanced accuracy, test = p5 only). With p6 the test was 64 %.
- One fixed threshold works while the rest level stays like in training. It fails when the rest level rises, as in p6. New electrodes will change the rest level, so the threshold must be measured against a short calibration at rest.
- The labels come from the KICK events of the board, not from a cue. The final test needs labels from a cue video and new sessions with new electrodes.

## Figures

- `figures/results_confusion.png`: right and wrong answers in training, validation and test.
- `figures/results_histogram.png`: the size of the windows of each class and the threshold.
- `figures/results_test_timeline.png`: what the model says along each test recording.
