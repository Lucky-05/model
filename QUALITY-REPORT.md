# Quality report

Made with `python3 code/check_quality.py`. The raw files in `data/raw/` are untouched.

**Rule, written before any model score.** Reject a window if one of its samples sits at a limit of the converter (0 or 1023), or if more than 1 % of the samples of the recording are missing. Because we had no cue, a "window" is 1 s around each contraction that the board detected (0.3 s before its `KICK` event to 0.7 s after), on the channel where it was detected.

| File | Seconds | Missing % | Ch1 at 0 % | Ch1 at 1023 % | Ch1 max | Ch1 windows (rejected) | Ch2 at 0 % | Ch2 at 1023 % | Ch2 max | Ch2 windows (rejected) |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-19_101044_p1_senal.csv | 52.7 | 0.7 | 28.9 | 0.00 | 331 | 3 (3) | 92.1 | 0.00 | 7 | 0 (0) |
| 2026-11-19_101935_p2_senal.csv | 26.0 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 69.0 | 0.00 | 140 | 2 (2) |
| 2026-11-19_105551_p3_senal.csv | 118.6 | 0.3 | 100.0 | 0.00 | 0 | 0 (0) | 41.0 | 0.00 | 166 | 24 (24) |
| 2026-11-19_110757_p4_senal.csv | 94.4 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 62.9 | 0.00 | 154 | 20 (20) |
| 2026-11-19_111517_p5_senal.csv | 130.3 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 62.7 | 0.00 | 136 | 23 (23) |
| 2026-11-19_112400_p6_senal.csv | 102.1 | 0.0 | 100.0 | 0.00 | 0 | 0 (0) | 21.2 | 0.00 | 148 | 2 (2) |
| 2026-11-24_203041_contracciones1_senal.csv | 96.2 | 0.8 | 0.0 | 0.00 | 996 | 0 (0) | 0.0 | 0.00 | 157 | 15 (0) |
| 2026-11-24_203532_contracciones2_senal.csv | 19.4 | 2.9 | 0.0 | 0.00 | 992 | 0 (0) | 0.0 | 0.00 | 113 | 3 (0) |
| 2026-11-24_204315_contracciones3_senal.csv | 113.7 | 0.3 | 0.0 | 0.00 | 982 | 0 (0) | 0.0 | 0.00 | 160 | 20 (0) |
| 2026-11-24_205100_contracciones4_senal.csv | 103.9 | 0.0 | 0.0 | 0.00 | 979 | 0 (0) | 0.0 | 0.00 | 185 | 17 (0) |
| 2026-11-24_205458_contracciones5_senal.csv | 74.1 | 0.0 | 0.0 | 0.00 | 978 | 0 (0) | 0.0 | 0.00 | 176 | 12 (0) |
| 2026-11-24_215819_prueba2canales_senal.csv | 59.4 | 0.9 | 0.0 | 0.00 | 158 | 0 (0) | 0.0 | 0.00 | 138 | 0 (0) |

Total: 12 recordings, 991 s, 141 detected windows, 74 rejected, 67 kept.

**Session S01 (19 Nov): 74 of 74 windows rejected with the rule as written.** The output of our amplifier rested near 0 V and had no offset. The ESP32 cannot read negative voltage, so the lower half of the signal was cut at 0 (21 % to 69 % of the samples of the active channel sit at 0). This is an artifact of our circuit, not of single trials. For S01 we use a changed rule: the lower limit does not reject. Then 0 of 74 are rejected, and the model sees a half-cut signal there.

**Session S02 (24 Nov): 0 of 67 windows rejected.** No sample at 0 or at 1023 on the channel we use. The signal rests at about 30 counts (0.09 V), not at mid scale, so part of its lower half is still cut without reaching 0. Channel 1 sat near the upper limit (about 980 counts, flat) in contracciones1 to 5: one pin of the ESP32 was damaged. We do not use channel 1 of those recordings. The board was replaced before prueba2canales.

**Gaps.** Missing samples are 0.0 % to 0.9 % per recording, except contracciones2 (2.9 %). That recording lasts 19 s and our clock has steps of 1 s, so its number is not precise; we keep it and note it.

**Noise.** Size of the signal at rest against movement, in windows of 0.25 s after the filters: S01, 0.7 to 1.9 counts at rest and 5 to 7 in movement. S02, 0.4 to 1.2 counts at rest and up to 12 in movement. See `figures/results_histogram.png`.

**Outliers.** p1: signal on the other channel (quadriceps). p6: rest level 3.5 counts and only 2 detections for about 12 contractions; taken out on 2026-11-23 after we saw its test score (`RESULTS.md` of that version). contracciones2: stopped after 19 s, one contraction.
