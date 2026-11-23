# Quality report

Made with `python3 code/check_quality.py`. The raw files in `data/raw/` are untouched.

**Rule, written before any model score.** Reject a window if one of its samples sits at a limit of the converter (0 or 1023), or if more than 1 % of the samples of the recording are missing. Because we had no cue on 19 Nov, a "window" is 1 s around each contraction that the board detected (0.3 s before its `KICK` event to 0.7 s after), on the channel where it was detected.

| File | Seconds | Missing % | Ch1 at 0 % | Ch1 at 1023 % | Ch1 max | Ch1 windows (rejected) | Ch2 at 0 % | Ch2 at 1023 % | Ch2 max | Ch2 windows (rejected) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-19_101044_p1_senal.csv | 52.7 | 0.7 | 28.9 | 0.00 | 331 | 3 (3) | 92.1 | 0.00 | 7 | 0 (0) |
| 2026-11-19_101935_p2_senal.csv | 26.0 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 69.0 | 0.00 | 140 | 2 (2) |
| 2026-11-19_105551_p3_senal.csv | 118.6 | 0.3 | 100.0 | 0.00 | 0 | 0 (0) | 41.0 | 0.00 | 166 | 24 (24) |
| 2026-11-19_110757_p4_senal.csv | 94.4 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 62.9 | 0.00 | 154 | 20 (20) |
| 2026-11-19_111517_p5_senal.csv | 130.3 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 62.7 | 0.00 | 136 | 23 (23) |
| 2026-11-19_112400_p6_senal.csv | 102.1 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 21.2 | 0.00 | 148 | 2 (2) |

Total: 6 recordings, 524 s, 74 detected windows, 74 rejected, 0 kept.

**Result with the rule as written: 74 of 74 windows rejected.** Every window has samples at 0.

**Why.** On 19 Nov the output of our amplifier rested near 0 V and had no offset. The ESP32 cannot read negative voltage, so the lower half of the signal was cut at 0 in every recording (21 % to 69 % of the samples of the active channel sit at 0). This is an artifact of our circuit, not of single trials. No sample reached the upper limit: the largest value is 331 of 1023.

**Gaps.** Missing samples are 0.0 % to 0.7 % per recording (sample count against the wall clock, which has steps of 1 s). No recording passes the 1 % limit.

**Noise.** After the band-pass and the notch (see `PROTOCOL.md`), in windows of 0.25 s of the training recordings p3 and p4: median size at rest 1.85 and 0.71 counts, median size during movement 7.26 and 5.22 counts. See `figures/two_features.png`.

**Outliers.** p1 has its signal on channel 1, all the others on channel 2. p2 is short (26 s) and p6 has only 2 detections in 102 s. p1 is the other channel, so another muscle; it is not used for the model. TODO(team): say what was different in p2 and p6.

**What we do about it.** Both, in two steps:
- Now, for the first version: we keep the recordings of 19 Nov and change the rule. The lower limit does not reject, because the signal rested there. The upper limit and gaps still reject. With this rule 0 of 74 windows are rejected. The model learns from a half-cut signal, and we say so.
- Next sessions: recorded with the 1.65 V offset and a cue video, and the rule as written applies again.
