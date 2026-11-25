# Protocol

Written so that a person outside the group can repeat the recording. Lines marked TODO(team) are facts only the team knows.

1. **Sensor and site.** Each channel of the board is one muscle: channel 1 quadriceps (p1), channel 2 hamstrings (p2 to p6). TODO(team): electrode type, distance between electrodes in cm, the muscle and side of each channel, position of the reference electrode, skin preparation, source for the position (for example the SENIAM recommendation for that muscle). Sensor: our own amplifier (pre-amplifier and analog band-pass filter). TODO(team): gain and the limits of the analog filter.
2. **Posture.** TODO(team).
3. **Task.** Contract the hamstrings and hold about 3 s, then relax. TODO(team): the exact movement of the leg. Two classes: movement and rest.
4. **Trial.** On 19 Nov there was no fixed timing. The person contracted when the penalty game asked for a kick. In recording p4 the contractions last about 3 s and repeat about every 8.6 s. TODO(team): the timing of the cue video for the next recordings (rest, warning, movement, rest between).
5. **Recording.** S01: 6 recordings of 26 s to 130 s on 2026-11-19 between 10:10 and 11:26. S02: 6 recordings of 19 s to 114 s on 2026-11-24 between 20:30 and 22:00, 10 or 15 contractions each, self-paced.
6. **Cue.** None on 19 Nov. TODO(team): `cue/cue-video.mp4`.
7. **Session.** Two sessions so far: S01 (19 Nov) and S02 (24 Nov). The recordings of one session share one electrode placement. Each session starts with new electrodes, placed again from zero, on another day.
8. **Settings.** ESP32, converter of 12 bits, input range 0 to 1.1 V in S01 and 0 to 3.1 V in S02, 8 readings averaged per sample, 1000 samples per second. The values are stored as counts of 10 bits (0 to 1023): volts = counts / 1023 x vref, with vref in `*_sesion.json`. Files per recording in `data/raw/`: `*_senal.csv` (muestra, t_s, canal1, canal2), `*_eventos.csv` (the `KICK` events of the board), `*_envolventes.csv` (the envelope and threshold the board computed), `*_sesion.json`.
9. **Filters, in this order** (`code/make_figures.py`; applied to a copy, never to the raw file):
   1. Band-pass, Butterworth, order 4, 20 Hz to 450 Hz, applied forward and backward (zero phase). 450 Hz is below half of our sampling rate (500 Hz). Source for 20 Hz: De Luca, Gilmore, Kuznetsov and Roy, "Filtering the surface EMG signal: movement artifact and baseline noise contamination", Journal of Biomechanics 43 (2010). Source for the upper limit: Merletti, "Standards for Reporting EMG Data", ISEK, 1999. TODO(team): open both and check that we quote them correctly.
   2. Notch at 60 Hz, quality factor 30, forward and backward. 60 Hz is the power line in Mexico.
   The signal is raw, not smoothed. The board also computes an envelope for the game (high-pass 20 Hz, notches at 60 Hz and its harmonics up to 480 Hz, rectifier, low-pass 5 Hz); we store it but do not use it as the raw data.
10. **Repeat a recording when** an electrode comes loose, the file has more than 1 % of samples missing, or the signal sits at a limit of the converter.
11. **Consent.** The participant agreed to the recording. We use codes, never names.

## We read the method and we agree
Each member adds their own line from their own GitHub account.

- TODO(member code), date, I read the method and I agree.
