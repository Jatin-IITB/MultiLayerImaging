# Prompt 03 - gate, classifiers, decision boundaries (track A, code c95604c)

Simulations: {'../archive/v1_mixed_projects/raw/brain_sevem_layer_Healthy.s6p': 'Normal', 'new_Healthy.s6p': 'Normal', 'new_MCI.s6p': 'MCI', '../archive/v1_mixed_projects/raw/Brain_sevem_layer_MildAD.s6p': 'Mild', 'new_MildAD.s6p': 'Mild', '../archive/v1_mixed_projects/raw/Brain_sevem_layer_ModerateAD.s6p': 'Moderate', 'new_ModerateAD.s6p': 'Moderate', '../archive/v1_mixed_projects/raw/brain_sevem_layer_SevereAD.s6p': 'Severe', 'new_SevereAD.s6p': 'Severe'}. Schemes run: ['binary', 'three_merged', 'three', 'binary_early']. Skipped: {}. Noise reference: mesh.
Validity: cross-solve-same-head, noise-robustness-only. Samples are antenna views of one simulation per stage; views are not independent. Band-averaged transmission powers are floor-subtracted: True.

## Instrument floor
Estimated from reciprocal-pair differences on the weakest paths (median over clean test measurements); the gate limit is τ(training) − 8.0 dB.
| profile | floor_db_median | floor_limit_db | tau_gate_db |
|---|---|---|---|
| ideal | -89.61 | -60.68 | -52.68 |
| good | -79.84 | -60.71 | -52.71 |
| typical | -69.93 | -60.72 | -52.72 |
| noisy | -60.06 | -60.58 | -52.58 |
| very_noisy | -51.29 | -58.78 | -50.78 |
| typical_jitter | -69.93 | -60.66 | -52.66 |
| typical+gain0.5dB | -69.92 | -60.59 | -52.59 |
| typical+gain1.0dB | -69.94 | -60.67 | -52.67 |
| typical+gain2.0dB | -69.94 | -60.77 | -52.77 |

## Quality gate: INVALID rate (expected ~0 for clean/shift/flatten, ~1 for detune/open/short; 'floor' rejects whole profiles whose floor is within 8 dB of τ)
| case | ideal | good | typical | noisy | very_noisy | typical_jitter | typical+gain0.5dB | typical+gain1.0dB | typical+gain2.0dB |
|---|---|---|---|---|---|---|---|---|---|
| clean | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.083 | 0.719 | 0.975 |
| shift-2MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.083 | 0.719 | 0.978 |
| shift+2MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.083 | 0.719 | 0.975 |
| shift-5MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.086 | 0.725 | 0.978 |
| shift+5MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.719 | 0.972 |
| shift-10MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.086 | 0.728 | 0.978 |
| shift+10MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.719 | 0.972 |
| shift-20MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.089 | 0.742 | 0.978 |
| shift+20MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.711 | 0.972 |
| flatten_notch | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.089 | 0.744 | 0.975 |
| detune-200MHz | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.989 | 0.769 | 0.975 |
| detune+200MHz | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.964 |
| one_open | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| one_short | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| open_all | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| short_all | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Reasons (typical, and clean draws of every profile):
| profile | case | invalid_rate | open_short | passivity | reciprocity | symmetry | detune | floor |
|---|---|---|---|---|---|---|---|---|
| ideal | clean | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| good | clean | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical | clean | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical | detune+200MHz | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| typical | one_open | 1.000 | 1.000 | 0.014 | 0.000 | 1.000 | 0.075 | 0.000 |
| typical | one_short | 1.000 | 1.000 | 0.014 | 0.000 | 1.000 | 0.075 | 0.000 |
| noisy | clean | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| very_noisy | clean | 1.000 | 0.000 | 0.025 | 0.000 | 0.000 | 0.000 | 1.000 |
| typical_jitter | clean | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical+gain0.5dB | clean | 0.083 | 0.000 | 0.083 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical+gain1.0dB | clean | 0.719 | 0.000 | 0.714 | 0.000 | 0.256 | 0.000 | 0.000 |
| typical+gain2.0dB | clean | 0.975 | 0.650 | 0.928 | 0.000 | 0.933 | 0.025 | 0.000 |

## Gain-invariant gate (for calibration-free R31): INVALID rate
| case | ideal | good | typical | noisy | very_noisy | typical_jitter | typical+gain0.5dB | typical+gain1.0dB | typical+gain2.0dB |
|---|---|---|---|---|---|---|---|---|---|
| clean | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift-2MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift+2MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift-5MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift+5MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift-10MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift+10MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift-20MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| shift+20MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| flatten_notch | 0.000 | 0.008 | 0.053 | 1.000 | 1.000 | 0.053 | 0.047 | 0.036 | 0.039 |
| detune-200MHz | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| detune+200MHz | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| one_open | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| one_short | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| open_all | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| short_all | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

## Complete decision rule scored per measurement (binary, same folds)
gate -> τ ± m (refit per fold) -> majority vote of 6 views (C3) or single value (ring-mean C3, R31). sensitivity/specificity count UNCERTAIN as not correct; *_decided are on non-UNCERTAIN measurements; rates are over valid (gate-passed) measurements. Normal has one simulation, so its test measurements are new noise draws of it.
| rule | gate_mode | profile | sensitivity | specificity | uncertain_rate | invalid_rate | sensitivity_decided | specificity_decided | tau_dB_mean | tau_dB_min | tau_dB_max | margin_dB_mean |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M5.C3 ring-mean | full | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.477 | -52.548 | -52.403 | 0.178 |
| M5.C3 ring-mean | full | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.472 | -52.520 | -52.434 | 0.180 |
| M5.C3 ring-mean | full | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.462 | -52.550 | -52.378 | 0.177 |
| M5.C3 ring-mean | full | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.506 | -52.592 | -52.438 | 0.177 |
| M5.C3 ring-mean | full | typical+gain0.5dB | 0.976 | 0.855 | 0.055 | 0.090 | 1.000 | 1.000 | -52.461 | -52.598 | -52.227 | 0.220 |
| M5.C3 ring-mean | full | typical+gain1.0dB | 0.957 | 0.730 | 0.101 | 0.731 | 1.000 | 0.964 | -52.666 | -52.713 | -52.492 | 0.308 |
| M5.C3 ring-mean | full | typical+gain2.0dB | 1.000 | 0.000 | 0.059 | 0.965 | 1.000 | 0.000 | -52.406 | -52.608 | -52.136 | 0.562 |
| M5.C3 ring-mean | full | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.476 | -52.553 | -52.410 | 0.182 |
| M5.C3 ring-mean | full | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -50.914 | -50.937 | -50.761 | 0.155 |
| M5.C3 ring-mean | gain_invariant | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.477 | -52.548 | -52.403 | 0.178 |
| M5.C3 ring-mean | gain_invariant | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.472 | -52.520 | -52.434 | 0.180 |
| M5.C3 ring-mean | gain_invariant | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.462 | -52.550 | -52.378 | 0.177 |
| M5.C3 ring-mean | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.506 | -52.592 | -52.438 | 0.177 |
| M5.C3 ring-mean | gain_invariant | typical+gain0.5dB | 0.975 | 0.867 | 0.052 | 0.000 | 1.000 | 1.000 | -52.461 | -52.598 | -52.227 | 0.220 |
| M5.C3 ring-mean | gain_invariant | typical+gain1.0dB | 0.819 | 0.883 | 0.148 | 0.000 | 0.977 | 0.991 | -52.666 | -52.713 | -52.492 | 0.308 |
| M5.C3 ring-mean | gain_invariant | typical+gain2.0dB | 0.669 | 0.525 | 0.298 | 0.000 | 0.923 | 0.829 | -52.406 | -52.608 | -52.136 | 0.562 |
| M5.C3 ring-mean | gain_invariant | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.476 | -52.553 | -52.410 | 0.182 |
| M5.C3 ring-mean | gain_invariant | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -50.914 | -50.937 | -50.761 | 0.155 |
| M5.C3 vote(6 views) | full | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.725 | -52.787 | -52.558 | 0.252 |
| M5.C3 vote(6 views) | full | ideal | 0.997 | 1.000 | 0.002 | 0.000 | 1.000 | 1.000 | -52.691 | -52.777 | -52.603 | 0.255 |
| M5.C3 vote(6 views) | full | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.578 | -52.591 | -52.534 | 0.268 |
| M5.C3 vote(6 views) | full | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.705 | -52.743 | -52.541 | 0.252 |
| M5.C3 vote(6 views) | full | typical+gain0.5dB | 0.988 | 1.000 | 0.009 | 0.090 | 1.000 | 1.000 | -52.524 | -52.633 | -52.426 | 0.331 |
| M5.C3 vote(6 views) | full | typical+gain1.0dB | 0.978 | 0.730 | 0.054 | 0.731 | 0.989 | 0.871 | -52.664 | -52.727 | -52.541 | 0.496 |
| M5.C3 vote(6 views) | full | typical+gain2.0dB | 1.000 | 0.000 | 0.176 | 0.965 | 1.000 | 0.000 | -52.873 | -53.287 | -52.806 | 1.369 |
| M5.C3 vote(6 views) | full | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.725 | -52.764 | -52.697 | 0.258 |
| M5.C3 vote(6 views) | full | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -50.778 | -50.780 | -50.774 | 0.341 |
| M5.C3 vote(6 views) | gain_invariant | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.725 | -52.787 | -52.558 | 0.252 |
| M5.C3 vote(6 views) | gain_invariant | ideal | 0.997 | 1.000 | 0.002 | 0.000 | 1.000 | 1.000 | -52.691 | -52.777 | -52.603 | 0.255 |
| M5.C3 vote(6 views) | gain_invariant | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.578 | -52.591 | -52.534 | 0.268 |
| M5.C3 vote(6 views) | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.705 | -52.743 | -52.541 | 0.252 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain0.5dB | 0.983 | 1.000 | 0.013 | 0.000 | 1.000 | 1.000 | -52.524 | -52.633 | -52.426 | 0.331 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain1.0dB | 0.861 | 0.892 | 0.083 | 0.000 | 0.945 | 0.955 | -52.664 | -52.727 | -52.541 | 0.496 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain2.0dB | 0.597 | 0.767 | 0.231 | 0.000 | 0.802 | 0.911 | -52.873 | -53.287 | -52.806 | 1.369 |
| M5.C3 vote(6 views) | gain_invariant | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.725 | -52.764 | -52.697 | 0.258 |
| M5.C3 vote(6 views) | gain_invariant | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -50.778 | -50.780 | -50.774 | 0.341 |
| M5.R31 | full | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.245 | -15.261 | -15.159 | 0.076 |
| M5.R31 | full | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.247 | -15.262 | -15.161 | 0.077 |
| M5.R31 | full | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -15.196 | -15.243 | -15.122 | 0.086 |
| M5.R31 | full | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.245 | -15.269 | -15.158 | 0.078 |
| M5.R31 | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.090 | 1.000 | 1.000 | -15.254 | -15.271 | -15.172 | 0.080 |
| M5.R31 | full | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.731 | 1.000 | 1.000 | -15.249 | -15.266 | -15.154 | 0.078 |
| M5.R31 | full | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.965 | 1.000 | 1.000 | -15.230 | -15.254 | -15.148 | 0.078 |
| M5.R31 | full | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.249 | -15.275 | -15.155 | 0.078 |
| M5.R31 | full | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -13.708 | -13.817 | -13.631 | 0.142 |
| M5.R31 | gain_invariant | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.245 | -15.261 | -15.159 | 0.076 |
| M5.R31 | gain_invariant | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.247 | -15.262 | -15.161 | 0.077 |
| M5.R31 | gain_invariant | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -15.196 | -15.243 | -15.122 | 0.086 |
| M5.R31 | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.245 | -15.269 | -15.158 | 0.078 |
| M5.R31 | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.254 | -15.271 | -15.172 | 0.080 |
| M5.R31 | gain_invariant | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.249 | -15.266 | -15.154 | 0.078 |
| M5.R31 | gain_invariant | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.230 | -15.254 | -15.148 | 0.078 |
| M5.R31 | gain_invariant | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.249 | -15.275 | -15.155 | 0.078 |
| M5.R31 | gain_invariant | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -13.708 | -13.817 | -13.631 | 0.142 |

## `binary` at `typical` (top 12 by balanced accuracy + M0)
CV: LOSO (8 folds), cross-solve-same-head.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| M9 | LDA | 1 | 1 | 1 | 0.00174 | 1 | 0 |  |
| M5.C3[nested] | kNN | 1 | 1 | 1 | 0 | 1 | 0 | windows 3.45-3.55×7, 3.30-3.55×1 |
| M5.C3[nested] | THR | 1 | 1 | 1 | 0.00243 | 1 | 0 | windows 3.45-3.55×7, 3.30-3.55×1 |
| M5 | LDA | 0.999 | 1 | 1 | 0.000694 | 1 | 0 |  |
| COMB | LSVM | 0.999 | 1 | 1 | 0.000694 | 1 | 0 | chosen M5.C3+M5.C2+M7.D2×4; M5.C3+M5.C2+M6.A[3.40]×3; M5.C3+M5.C2+M6.A[3.65]×1 |
| M6 | LDA | 0.999 | 1 | 1 | 0.00104 | 0.999 | 0 |  |
| M5 | LSVM | 0.999 | 1 | 1 | 0.000694 | 1 | 0 |  |
| M5.C3[nested] | LSVM | 0.999 | 0.999 | 0.999 | 0 | 1 | 0 | windows 3.45-3.55×7, 3.30-3.55×1 |
| M5.C3[k3] | THR | 0.999 | 0.998 | 0.997 | 0.00278 | 0.999 | 0 |  |
| M5.C3[k3] | kNN | 0.998 | 0.999 | 0.999 | 0.00104 | 0.999 | 0 |  |
| M5.C3[nested] | ORD | 0.997 | 0.999 | 0.998 | 0.00174 | 1 | 0 | windows 3.45-3.55×7, 3.30-3.55×1 |
| COMB | LDA | 0.997 | 0.999 | 0.998 | 0.00313 | 0.997 | 0 | chosen M5.C3+M5.C2+M7.D2×4; M5.C3+M5.C2+M6.A[3.40]×3; M5.C3+M5.C2+M6.A[3.65]×1 |
| M0 | LDA | 0.62 | 0.628 | 0.584 | 0.773 | 0.769 | 0 |  |
| M0 | LR | 0.62 | 0.628 | 0.584 | 0.74 | 0.743 | 0 |  |
| M0 | LSVM | 0.62 | 0.628 | 0.584 | 0.768 | 0.767 | 0 |  |
| M0 | ORD | 0.62 | 0.628 | 0.584 | 0.77 | 0.769 | 0 |  |
| M0 | THR | 0.619 | 0.622 | 0.58 | 0.77 | 0.774 | 0 |  |
| M0 | RBF | 0.617 | 0.634 | 0.586 | 1 | n/a | 0 |  |
| M0 | kNN | 0.602 | 0.608 | 0.566 | 0.932 | 0.693 | 0 |  |

## `three_merged` at `typical` (top 12 by balanced accuracy + M0)
CV: LOSO (8 folds), cross-solve-same-head.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| M5 | LDA | 0.98 | 0.973 | 0.974 | 0.00764 | 0.984 | 0 |  |
| M9 | LDA | 0.978 | 0.984 | 0.983 | 0.0292 | 0.981 | 0 |  |
| M5 | LR | 0.976 | 0.969 | 0.97 | 0.0122 | 0.95 | 0 |  |
| M5 | kNN | 0.971 | 0.965 | 0.966 | 0.0271 | 0.983 | 0 |  |
| M6 | LDA | 0.97 | 0.968 | 0.969 | 0.0722 | 0.929 | 0 |  |
| M5 | RBF | 0.96 | 0.957 | 0.957 | 0.00208 | 0.96 | 0 |  |
| M5 | LSVM | 0.948 | 0.942 | 0.943 | 0.0101 | 0.974 | 0 |  |
| M5 | ORD | 0.939 | 0.94 | 0.94 | 0.0323 | 0.929 | 0 |  |
| M9 | ORD | 0.934 | 0.95 | 0.948 | 0.0271 | 0.966 | 0 |  |
| COMB | LDA | 0.832 | 0.824 | 0.826 | 0.0889 | 0.827 | 0 | chosen M5.C2+M5.C+M7.D2×2; M5.C2+M5.C+M6.A[3.40]×1; M5.C2+M6.A[3.35]+M6.A[3.70]×1; M5.C2+M6.A[3.60]+M6.A[3.55]×1; M5.C2+M6.A[3.60]+M6.A[3.40]×1; M5.C2+M7.D2+M6.A[3.65]×1; M5.C2+M6.A[3.40]+M6.A[3.60]×1 |
| M9 | LR | 0.8 | 0.845 | 0.828 | 0.0226 | 0.866 | 0 |  |
| M9 | LSVM | 0.781 | 0.812 | 0.804 | 0.0208 | 0.928 | 0 |  |
| M0 | kNN | 0.425 | 0.4 | 0.397 | 0.998 | n/a | 0 |  |
| M0 | RBF | 0.422 | 0.327 | 0.307 | 1 | n/a | 0 |  |
| M0 | ORD | 0.42 | 0.361 | 0.363 | 0.989 | 0.333 | 0 |  |
| M0 | LR | 0.345 | 0.292 | 0.291 | 0.983 | 0.333 | 0 |  |
| M0 | LDA | 0.342 | 0.29 | 0.29 | 0.988 | 0.333 | 0 |  |
| M0 | LSVM | 0.322 | 0.403 | 0.278 | 0.988 | 0.333 | 0 |  |

## `three` at `typical` (top 12 by balanced accuracy + M0)
CV: LOSO (6 folds), cross-solve-same-head.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| M5 | LDA | 0.961 | 0.961 | 0.961 | 0.00602 | 0.962 | 0 |  |
| M5 | LR | 0.942 | 0.942 | 0.942 | 0.0255 | 0.903 | 0 |  |
| M9 | ORD | 0.925 | 0.925 | 0.924 | 0.069 | 0.948 | 0 |  |
| M5 | ORD | 0.899 | 0.899 | 0.899 | 0.0403 | 0.882 | 0 |  |
| M5 | LSVM | 0.894 | 0.894 | 0.893 | 0.0144 | 0.935 | 0 |  |
| M5 | kNN | 0.889 | 0.889 | 0.885 | 0.0616 | 0.882 | 0 |  |
| M5 | RBF | 0.886 | 0.886 | 0.883 | 0.0259 | 0.91 | 0 |  |
| COMB | LDA | 0.868 | 0.868 | 0.87 | 0.125 | 0.769 | 0 | chosen M5.C2+M5.C+M6.A[3.40]×1; M5.C2+M6.A[3.35]+M6.A[3.60]×1; M5.C2+M5.C3+M6.A[3.65]×1; M5.C2+M5.C1+M7.D2×1; M5.C2+M7.D2+M6.A[3.65]×1; M5.C2+M6.A[3.60]+M6.A[3.40]×1 |
| M9 | LDA | 0.797 | 0.797 | 0.794 | 0.117 | 0.743 | 0 |  |
| COMB | ORD | 0.773 | 0.773 | 0.78 | 0.144 | 0.759 | 0 | chosen M5.C2+M5.C+M6.A[3.40]×1; M5.C2+M6.A[3.35]+M6.A[3.60]×1; M5.C2+M5.C3+M6.A[3.65]×1; M5.C2+M5.C1+M7.D2×1; M5.C2+M7.D2+M6.A[3.65]×1; M5.C2+M6.A[3.60]+M6.A[3.40]×1 |
| M6 | LDA | 0.711 | 0.711 | 0.709 | 0.115 | 0.542 | 0 |  |
| M5.C3 | ORD | 0.662 | 0.662 | 0.664 | 0.573 | 0.341 | 0 |  |
| M0 | kNN | 0.419 | 0.419 | 0.414 | 0.996 | n/a | 0 |  |
| M0 | ORD | 0.419 | 0.419 | 0.399 | 0.984 | 0.333 | 0 |  |
| M0 | RBF | 0.406 | 0.406 | 0.374 | 1 | n/a | 0 |  |
| M0 | LDA | 0.388 | 0.388 | 0.376 | 0.983 | 0.333 | 0 |  |
| M0 | LR | 0.387 | 0.387 | 0.375 | 0.982 | 0.333 | 0 |  |
| M0 | LSVM | 0.176 | 0.176 | 0.154 | 0.983 | 0.333 | 0 |  |

## `binary_early` at `typical` (top 12 by balanced accuracy + M0)
CV: LODO+LOSO-within-class (6 folds), noise-robustness-only.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| COMB | LDA | 1 | 1 | 1 | 0.00208 | 1 | 0 | chosen M6.A[3.60]+M6.A[3.40]+M7.D2×3; M6.A[3.60]+M6.A[3.45]+M6.A[3.55]×2; M6.A[3.60]+M6.A[3.45]+M6.A[3.50]×1 |
| COMB | LSVM | 0.988 | 0.988 | 0.987 | 0.0292 | 0.996 | 0 | chosen M6.A[3.60]+M6.A[3.40]+M7.D2×3; M6.A[3.60]+M6.A[3.45]+M6.A[3.55]×2; M6.A[3.60]+M6.A[3.45]+M6.A[3.50]×1 |
| COMB | kNN | 0.975 | 0.975 | 0.975 | 0.0278 | 0.979 | 0 | chosen M6.A[3.60]+M6.A[3.40]+M7.D2×3; M6.A[3.60]+M6.A[3.45]+M6.A[3.55]×2; M6.A[3.60]+M6.A[3.45]+M6.A[3.50]×1 |
| COMB | ORD | 0.951 | 0.951 | 0.951 | 0.0625 | 0.975 | 0 | chosen M6.A[3.60]+M6.A[3.40]+M7.D2×3; M6.A[3.60]+M6.A[3.45]+M6.A[3.55]×2; M6.A[3.60]+M6.A[3.45]+M6.A[3.50]×1 |
| COMB | LR | 0.947 | 0.947 | 0.947 | 0.0632 | 0.957 | 0 | chosen M6.A[3.60]+M6.A[3.40]+M7.D2×3; M6.A[3.60]+M6.A[3.45]+M6.A[3.55]×2; M6.A[3.60]+M6.A[3.45]+M6.A[3.50]×1 |
| M6 | LDA | 0.912 | 0.912 | 0.911 | 0.17 | 0.958 | 0 |  |
| COMB | RBF | 0.881 | 0.881 | 0.88 | 0.192 | 0.834 | 0 | chosen M6.A[3.60]+M6.A[3.40]+M7.D2×3; M6.A[3.60]+M6.A[3.45]+M6.A[3.55]×2; M6.A[3.60]+M6.A[3.45]+M6.A[3.50]×1 |
| M5.C3[nested] | RBF | 0.874 | 0.874 | 0.872 | 0.0132 | 0.899 | 0 | windows 3.60-3.70×3, 3.80-4.00×2, 3.80-4.05×1 |
| M5.C3[nested] | kNN | 0.874 | 0.874 | 0.872 | 0.00417 | 0.903 | 0 | windows 3.60-3.70×3, 3.80-4.00×2, 3.80-4.05×1 |
| M5.C3[nested] | LSVM | 0.869 | 0.869 | 0.867 | 0.0208 | 0.896 | 0 | windows 3.60-3.70×3, 3.80-4.00×2, 3.80-4.05×1 |
| M5.C3[nested] | THR | 0.867 | 0.867 | 0.865 | 0.0264 | 0.89 | 0 | windows 3.60-3.70×3, 3.80-4.00×2, 3.80-4.05×1 |
| M5.C3[nested] | ORD | 0.861 | 0.861 | 0.859 | 0.0354 | 0.888 | 0 | windows 3.60-3.70×3, 3.80-4.00×2, 3.80-4.05×1 |
| M0 | kNN | 0.529 | 0.529 | 0.529 | 0.994 | 0.625 | 0 |  |
| M0 | THR | 0.514 | 0.514 | 0.512 | 1 | n/a | 0 |  |
| M0 | RBF | 0.513 | 0.513 | 0.51 | 1 | n/a | 0 |  |
| M0 | LR | 0.507 | 0.507 | 0.507 | 0.999 | n/a | 0 |  |
| M0 | LDA | 0.506 | 0.506 | 0.505 | 1 | n/a | 0 |  |
| M0 | LSVM | 0.506 | 0.506 | 0.505 | 1 | n/a | 0 |  |
| M0 | ORD | 0.506 | 0.506 | 0.505 | 1 | n/a | 0 |  |

## Per-port amplitude (gain) errors, binary, per view (balanced accuracy)
| feature_set | model | no gain error | typical+gain0.5dB | typical+gain1.0dB | typical+gain2.0dB |
|---|---|---|---|---|---|
| COMB | LR | 0.994 | 0.960 | 0.928 | 0.501 |
| M0 | LR | 0.620 | 0.538 | 0.542 | 0.515 |
| M0 | THR | 0.619 | 0.472 | 0.405 | 0.464 |
| M5.C3 | LR | 0.984 | 0.942 | 0.849 | 0.526 |
| M5.C3 | THR | 0.983 | 0.932 | 0.848 | 0.589 |
| M5.C3[nested] | LR | 0.997 | 0.984 | 0.802 | 0.533 |
| M5.C3[nested] | THR | 1.000 | 0.983 | 0.834 | 0.567 |
| M9 | LR | 0.986 | 0.976 | 0.928 | 0.867 |

## Binary thresholds (Normal | AD), dB, per profile
τ = class-balanced (equal priors) error minimiser; τ_screen uses P(Normal) = 0.8; CI = bootstrap over simulations (within class), views and draws (1000×). Margin m = max(posterior margin at p* = 0.7, Φ⁻¹(p*)·σ_ref); σ_ref = within-simulation SD of one view (one measurement for R31) + between-mesh SD. M5.C3_raw = without floor subtraction. Sensitivity/specificity here are resubstitution.
| feature | profile | tau_dB | tau_CI_lo | tau_CI_hi | tau_screen_dB | margin_dB | sd_ref_dB | mu_Normal_dB | mu_AD_dB | sensitivity | specificity | uncertain_fraction |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M5.C3 | good | -52.67 | -52.88 | -52.52 | -52.79 | 0.2447 | 0.4666 | -51.74 | -53.56 | 0.9972 | 0.9958 | 0.02622 |
| M5.C3 | ideal | -52.72 | -52.78 | -52.57 | -52.72 | 0.2465 | 0.4701 | -51.75 | -53.57 | 0.9986 | 1 | 0.0349 |
| M5.C3 | noisy | -52.57 | -52.72 | -52.47 | -52.66 | 0.2627 | 0.5009 | -51.7 | -53.54 | 0.9947 | 0.9924 | 0.04878 |
| M5.C3 | typical | -52.71 | -52.83 | -52.51 | -52.79 | 0.2441 | 0.4655 | -51.74 | -53.57 | 0.9965 | 0.9979 | 0.03507 |
| M5.C3 | typical+gain0.5dB | -52.66 | -52.7 | -52.39 | -52.9 | 0.3278 | 0.6251 | -51.74 | -53.56 | 0.9336 | 0.9611 | 0.166 |
| M5.C3 | typical+gain1.0dB | -52.61 | -52.78 | -52.5 | -53.53 | 0.4976 | 0.9489 | -51.78 | -53.58 | 0.8398 | 0.8194 | 0.2566 |
| M5.C3 | typical+gain2.0dB | -52.86 | -53.29 | -51.99 | -54.78 | 1.378 | 1.745 | -51.72 | -53.51 | 0.6366 | 0.7458 | 0.5122 |
| M5.C3 | typical_jitter | -52.61 | -52.78 | -52.53 | -52.74 | 0.2496 | 0.4759 | -51.74 | -53.57 | 0.9995 | 0.9986 | 0.02361 |
| M5.C3 | very_noisy | -50.79 | -50.92 | -50.75 | -51.29 | 0.3352 | 0.6392 | -50.28 | -51.52 | 0.8785 | 0.8354 | 0.2512 |
| M5.C3[k3] | good | -48.61 | -48.78 | -48.51 | -48.61 | 0.3041 | 0.58 | -47.52 | -49.68 | 1 | 1 | 0.01858 |
| M5.C3[k3] | ideal | -48.62 | -48.69 | -48.58 | -48.62 | 0.3076 | 0.5865 | -47.53 | -49.69 | 1 | 1 | 0.01736 |
| M5.C3[k3] | noisy | -48.48 | -48.68 | -48.41 | -48.55 | 0.3283 | 0.626 | -47.49 | -49.67 | 0.9972 | 0.9958 | 0.04531 |
| M5.C3[k3] | typical | -48.52 | -48.65 | -48.45 | -48.52 | 0.3065 | 0.5844 | -47.52 | -49.69 | 1 | 1 | 0.01354 |
| M5.C3[k3] | typical+gain0.5dB | -48.51 | -48.68 | -48.35 | -48.74 | 0.3728 | 0.711 | -47.51 | -49.67 | 0.9715 | 0.9708 | 0.1233 |
| M5.C3[k3] | typical+gain1.0dB | -48.51 | -48.83 | -48.35 | -49.29 | 0.5304 | 1.011 | -47.55 | -49.7 | 0.8789 | 0.8528 | 0.2339 |
| M5.C3[k3] | typical+gain2.0dB | -48.86 | -49.07 | -48.61 | -50.56 | 1.174 | 1.782 | -47.49 | -49.62 | 0.66 | 0.7958 | 0.4236 |
| M5.C3[k3] | typical_jitter | -48.53 | -48.71 | -48.49 | -48.53 | 0.3122 | 0.5953 | -47.52 | -49.69 | 1 | 1 | 0.01059 |
| M5.C3[k3] | very_noisy | -47.73 | -47.91 | -47.43 | -48.14 | 0.4868 | 0.9282 | -46.89 | -48.72 | 0.8572 | 0.8757 | 0.2694 |
| M5.C3_raw | good | -52.66 | -52.87 | -52.52 | -52.78 | 0.2441 | 0.4656 | -51.73 | -53.55 | 0.9972 | 0.9958 | 0.02622 |
| M5.C3_raw | ideal | -52.72 | -52.78 | -52.57 | -52.72 | 0.2465 | 0.47 | -51.75 | -53.57 | 0.9986 | 1 | 0.0349 |
| M5.C3_raw | noisy | -51.87 | -51.99 | -51.78 | -51.99 | 0.2181 | 0.4158 | -51.11 | -52.66 | 0.9935 | 0.9931 | 0.05017 |
| M5.C3_raw | typical | -52.65 | -52.75 | -52.43 | -52.71 | 0.2388 | 0.4554 | -51.68 | -53.47 | 0.9956 | 0.9993 | 0.03976 |
| M5.C3_raw | typical+gain0.5dB | -52.58 | -52.61 | -52.34 | -52.75 | 0.3209 | 0.6119 | -51.67 | -53.46 | 0.9326 | 0.9618 | 0.1658 |
| M5.C3_raw | typical+gain1.0dB | -52.53 | -52.7 | -52.44 | -53.44 | 0.4874 | 0.9295 | -51.71 | -53.48 | 0.8398 | 0.8194 | 0.2559 |
| M5.C3_raw | typical+gain2.0dB | -52.79 | -53.2 | -51.92 | -54.65 | 1.352 | 1.708 | -51.65 | -53.4 | 0.6356 | 0.7472 | 0.5125 |
| M5.C3_raw | typical_jitter | -52.53 | -52.7 | -52.46 | -52.65 | 0.244 | 0.4654 | -51.67 | -53.47 | 0.9995 | 0.9986 | 0.02344 |
| M5.C3_raw | very_noisy | -48.02 | -48.09 | -47.97 | -48.29 | 0.1722 | 0.3283 | -47.74 | -48.38 | 0.8782 | 0.8306 | 0.2517 |
| M5.R31 | good | -15.26 | -15.36 | -15.16 | -15.54 | 0.0762 | 0.1453 | -14.58 | -16.1 | 1 | 1 | 0 |
| M5.R31 | ideal | -15.26 | -15.36 | -15.16 | -15.55 | 0.07665 | 0.1462 | -14.58 | -16.1 | 1 | 1 | 0 |
| M5.R31 | noisy | -15.22 | -15.38 | -15.1 | -15.38 | 0.08594 | 0.1639 | -14.56 | -16.1 | 1 | 1 | 0 |
| M5.R31 | typical | -15.27 | -15.37 | -15.17 | -15.53 | 0.07832 | 0.1494 | -14.58 | -16.11 | 1 | 1 | 0 |
| M5.R31 | typical+gain0.5dB | -15.25 | -15.35 | -15.15 | -15.51 | 0.08025 | 0.153 | -14.58 | -16.11 | 1 | 1 | 0 |
| M5.R31 | typical+gain1.0dB | -15.26 | -15.36 | -15.16 | -15.52 | 0.0778 | 0.1484 | -14.58 | -16.11 | 1 | 1 | 0 |
| M5.R31 | typical+gain2.0dB | -15.25 | -15.37 | -15.15 | -15.5 | 0.07843 | 0.1496 | -14.58 | -16.11 | 1 | 1 | 0 |
| M5.R31 | typical_jitter | -15.26 | -15.36 | -15.16 | -15.51 | 0.07819 | 0.1491 | -14.58 | -16.11 | 1 | 1 | 0 |
| M5.R31 | very_noisy | -13.67 | -13.87 | -13.57 | -13.82 | 0.1429 | 0.2725 | -13.28 | -14.23 | 0.95 | 0.9458 | 0.1042 |

### τ drift between profiles (dB)
| feature | tau_typical | drift_ideal..typical_jitter | tau_noisy - tau_typical | tau_very_noisy - tau_typical | max |tau(gain) - tau_typical| |
|---|---|---|---|---|---|
| M5.C3 | -52.715 | 0.103 | 0.141 | 1.929 | 0.150 |
| M5.C3[k3] | -48.523 | 0.094 | 0.039 | 0.795 | 0.334 |
| M5.C3_raw | -52.654 | 0.182 | 0.784 | 4.635 | 0.132 |
| M5.R31 | -15.273 | 0.016 | 0.055 | 1.599 | 0.022 |

### CV sensitivity / specificity of the fold-fitted threshold (THR, per view)
| profile | feature_set | cv_sensitivity | cv_specificity | fold_tau_dB_min | fold_tau_dB_max |
|---|---|---|---|---|---|
| ideal | M0 | 0.5097 | 0.6556 | -2.565 | -2.49 |
| ideal | M5.C3 | 0.9963 | 0.9944 | -52.78 | -52.6 |
| ideal | M5.C3[k3] | 1 | 1 | -48.73 | -48.68 |
| ideal | M5.C3[nested] | 0.9995 | 1 | -48.77 | -48.76 |
| good | M0 | 0.5884 | 0.6319 | -2.552 | -2.532 |
| good | M5.C3 | 0.9917 | 0.9889 | -52.79 | -52.56 |
| good | M5.C3[k3] | 0.9926 | 1 | -48.85 | -48.62 |
| good | M5.C3[nested] | 0.9907 | 1 | -48.71 | -48.1 |
| typical | M0 | 0.625 | 0.6125 | -2.573 | -2.549 |
| typical | M5.C3 | 0.994 | 0.9722 | -52.74 | -52.54 |
| typical | M5.C3[k3] | 0.9972 | 1 | -48.72 | -48.53 |
| typical | M5.C3[nested] | 0.9995 | 1 | -48.66 | -48.53 |
| noisy | M0 | n/a | n/a | -2.594 | -2.513 |
| noisy | M5.C3 | n/a | n/a | -52.59 | -52.53 |
| noisy | M5.C3[k3] | n/a | n/a | -48.54 | -48.42 |
| noisy | M5.C3[nested] | n/a | n/a | -48.54 | -48.16 |
| very_noisy | M0 | n/a | n/a | -2.611 | -2.52 |
| very_noisy | M5.C3 | n/a | n/a | -50.78 | -50.77 |
| very_noisy | M5.C3[k3] | n/a | n/a | -47.73 | -47.53 |
| very_noisy | M5.C3[nested] | n/a | n/a | -48.75 | -47.77 |
| typical_jitter | M0 | 0.494 | 0.7014 | -2.533 | -2.497 |
| typical_jitter | M5.C3 | 0.9963 | 1 | -52.76 | -52.7 |
| typical_jitter | M5.C3[k3] | 0.9991 | 1 | -48.71 | -48.69 |
| typical_jitter | M5.C3[nested] | 0.9986 | 1 | -48.68 | -48.31 |
| typical+gain0.5dB | M0 | 0.5979 | 0.347 | -3.144 | -2.203 |
| typical+gain0.5dB | M5.C3 | 0.9664 | 0.897 | -52.63 | -52.43 |
| typical+gain0.5dB | M5.C3[nested] | 0.9908 | 0.9742 | -48.45 | -48.31 |
| typical+gain1.0dB | M0 | 0.346 | 0.464 | -3.283 | -1.796 |
| typical+gain1.0dB | M5.C3 | 0.9475 | 0.7477 | -52.73 | -52.54 |
| typical+gain1.0dB | M5.C3[nested] | 0.9873 | 0.6802 | -50.17 | -48.7 |
| typical+gain2.0dB | M0 | 0.02778 | 0.9 | -1.369 | -1.339 |
| typical+gain2.0dB | M5.C3 | 0.9444 | 0.2333 | -53.29 | -52.81 |
| typical+gain2.0dB | M5.C3[nested] | 1 | 0.1333 | -49.93 | -49.05 |
