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

## 3. Test (recordings the model never saw: p5 and p6)

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p5 | 357 | 93% | 87% | 78% (54/69) | 97% (278/288) |
| p6 | 390 | 13% | 56% | 100% (6/6) | 12% (45/384) |
| all | 747 | 51% | 64% | 80% (60/75) | 48% (323/672) |

## What this shows

- Training 95 %, validation 86 %, test 64 % (balanced accuracy). The goal is more than 75 % on recordings never seen. p5 passes (87 %), p6 does not (56 %).
- Why p6 fails: its signal at rest is about 3.3 counts, above the threshold of 2.93, so the model says movement almost all the time. In p3 to p5 rest is 0.7 to 1.9 counts. One fixed threshold does not survive a change of the rest level.
- The labels of p6 are also wrong: the figure shows about 12 contractions, and the board wrote only 2 KICK events. Windows inside real contractions count as rest here. So the true score of p6 is unknown.
- The test recordings were opened on 2026-11-23. We do not tune the model on them. They are from the same session as the training recordings, so the final test will be new sessions with new electrodes.
- Next: labels from a cue video instead of the board, and a size measured against the rest level of each recording (a short calibration at rest), checked with validation only.

## Figures

- `figures/results_confusion.png`: right and wrong answers in training, validation and test.
- `figures/results_histogram.png`: the size of the windows of each class and the threshold.
- `figures/results_test_timeline.png`: what the model says along each test recording.
