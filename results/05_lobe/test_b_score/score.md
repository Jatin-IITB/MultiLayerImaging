# Test_B: main-session estimates (0f49389) scored against the truth, per protocol §3 (d3a4bbf) (code 6d60b2a-dirty)

Truth (user, returned after all estimates were committed): e = 0/11.5/0/0/7.5/0 mm, Mild materials in S2 and S5, HIP_Mild, CSF_Mild everywhere. Blobs of protocol.md and estimates.csv checked.

| item | estimate | truth | score | confidence as reported |
|---|---|---|---|---|
| detection | AD | AD (disease present) | correct | +0.094 dB; A1 0.70x; not determined (< 2x) |
| staging three (R21) | Normal | Mild | wrong | +0.122 dB; A1 1.11x; not determined (< 2x) |
| staging three_merged (R32) | Normal | Mild+Moderate | wrong | -0.025 dB; A1 0.16x; not determined (< 2x) |
| side | left | left ((e_S2+e_S3)-(e_S5+e_S6) = +4.0 mm) | correct | sensitive (mirror test only); fit side symmetric, mirror side left (7 votes >= 2x, 4 >= 3x) |
| S1 frontal | uncertain | not affected | uncertain (abstention) | 1.5x |
| S2 temporal L | uncertain | affected | uncertain (abstention) | 1.9x |
| S3 parietal L | uncertain | not affected | uncertain (abstention) | 1.0x |
| S4 occipital | uncertain | not affected | uncertain (abstention) | 1.8x |
| S5 parietal R | uncertain | affected | uncertain (abstention) | 1.1x |
| S6 temporal R | uncertain | not affected | uncertain (abstention) | 1.6x |
| sector pattern (best fit, reported) | 25 | 25 | equals the truth; exact under §3: False (§3 requires no uncertain sector) | fit accepted (accepted); contrast 3.2x null; ring mean -3.88 deg (3.5x healthy twin) |

Sector counts: {'hits': 0, 'misses': 0, 'false alarms': 0, 'correct rejections': 0, 'uncertain': 6}; pattern exact under §3: False.
Calibration: errors: staging three (R21) (+0.122 dB; A1 1.11x; not determined (< 2x)), staging three_merged (R32) (-0.025 dB; A1 0.16x; not determined (< 2x)). Calls marked established among the scored items: 0; every error sits on a label whose margin was 'not determined'.
