# Results of the model

Made with `python3 code/evaluate.py`.
Model: movement if the size of a window of 0.25 s (its mean absolute value) is above 2.44 times the rest level of the recording.
Balanced accuracy is the mean of "movement found" and "rest found". We use it because there is about 4 times more rest than movement.

## 1. Training (session S02, 24 Nov; the model sees these windows)

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| contracciones1 | 273 | 92% | 95% | 100% (45/45) | 91% (207/228) |
| contracciones2 | 59 | 100% | 100% | 100% (9/9) | 100% (50/50) |
| contracciones3 | 299 | 91% | 90% | 88% (53/60) | 92% (219/239) |
| contracciones4 | 271 | 91% | 90% | 88% (45/51) | 91% (201/220) |
| all | 902 | 92% | 92% | 92% (152/165) | 92% (677/737) |

## 2. Validation (leave one training recording out)

Each column: the model is set with the other training recordings, then checked on this one.

| Model | contracciones1 | contracciones2 | contracciones3 | contracciones4 | all held-out windows |
|---|---|---|---|---|---|
| threshold on the size (counts) | 93% | 94% | 92% | 92% | 92% |
| threshold on the size against rest (chosen) | 95% | 100% | 89% | 89% | 91% |
| logistic regression (size, waveform length, in counts) | 96% | 100% | 94% | 93% | 94% |
| logistic regression (size, waveform length, against rest) | 94% | 100% | 91% | 90% | 92% |
| decision tree, depth 2 (size, waveform length, in counts) | 96% | 100% | 92% | 93% | 94% |
| decision tree, depth 2 (size, waveform length, against rest) | 93% | 99% | 92% | 93% | 93% |

How we chose. The models "in counts" depend on the scale of the converter, and that scale changed between our sessions (0-1.1 V on 19 Nov, 0-3.1 V on 24 Nov), so they cannot be used on another session. Among the three models "against rest" the scores are 91 % to 93 %, a difference smaller than the change from one recording to the next. We keep the simplest one.

The chosen model in detail:

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| contracciones1 | 273 | 91% | 95% | 100% (45/45) | 89% (204/228) |
| contracciones2 | 59 | 100% | 100% | 100% (9/9) | 100% (50/50) |
| contracciones3 | 299 | 91% | 89% | 87% (52/60) | 92% (219/239) |
| contracciones4 | 271 | 91% | 89% | 86% (44/51) | 92% (202/220) |
| all | 902 | 91% | 91% | 91% (150/165) | 92% (675/737) |

## 3. Test A: same session, a recording never used to train

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| contracciones5 | 199 | 93% | 95% | 97% (35/36) | 93% (151/163) |

## 4. Test B: another session (S01, 19 Nov, other electrode placement)

| Recording | Windows | Accuracy | Balanced accuracy | Movement found | Rest found |
|---|---|---|---|---|---|
| p2 | 86 | 88% | 94% | 100% (6/6) | 88% (70/80) |
| p3 | 332 | 95% | 88% | 75% (54/72) | 100% (260/260) |
| p4 | 251 | 96% | 93% | 88% (53/60) | 98% (187/191) |
| p5 | 357 | 93% | 89% | 81% (56/69) | 96% (277/288) |
| all | 1026 | 94% | 89% | 82% (169/207) | 97% (794/819) |

Note: these recordings are not new to us. An earlier model was built and tested on them (see the history of this repository), and that is where the idea of measuring the size against the rest level came from. The model above was trained without them, on S02 only.
p1 (other muscle) and p6 (abnormal rest level and wrong labels, taken out on 2026-11-23 after we saw its score) are not used.

## What this shows

- Training 92%, validation 91%, test in the same session 95%, test in another session 89% (balanced accuracy). The goal is more than 75 % on sessions never seen.
- The same number works on two days with different electrodes and a different converter range, because the size is measured against the rest level of each recording.
- Limits: one person, two sessions, self-paced contractions. The labels come from the KICK events of the board, not from a cue video. The signal rests near the lower limit of the converter, so its lower half is cut.

## Figures

- `figures/results_confusion.png`: right and wrong answers in training, validation and the two tests.
- `figures/results_histogram.png`: the size of the windows of each class against the rest level, and the threshold.
- `figures/results_test_timeline.png`: what the model says along one test recording of each session.
