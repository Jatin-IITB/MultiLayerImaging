# Prompt 03 - gate, classifiers, decision boundaries (track A, code 45e16c6)

Simulations: {'brain_sevem_layer_Healthy.s6p': 'Normal', 'Brain_sevem_layer_MildAD.s6p': 'Mild', 'Brain_sevem_layer_ModerateAD.s6p': 'Moderate', 'brain_sevem_layer_SevereAD.s6p': 'Severe'}. Schemes run: ['binary', 'three_merged', 'three']. Skipped: {'binary_early': "no simulation for class(es) ['MCI']"}. Noise reference: port (between-mesh not measured: AD-vs-AD results unverified against mesh noise).
Validity: noise-robustness-only. Samples are antenna views of one simulation per stage; views are not independent. Band-averaged transmission powers are floor-subtracted: True.

## Instrument floor
Estimated from reciprocal-pair differences on the weakest paths (median over clean test measurements); the gate limit is τ(training) − 8.0 dB.
| profile | floor_db_median | floor_limit_db | tau_gate_db |
|---|---|---|---|
| ideal | -89.60 | -60.83 | -52.83 |
| good | -79.83 | -60.82 | -52.82 |
| typical | -69.94 | -60.76 | -52.76 |
| noisy | -60.05 | -60.66 | -52.66 |
| very_noisy | -51.32 | -58.91 | -50.91 |
| typical_jitter | -69.92 | -60.74 | -52.74 |
| typical+gain0.5dB | -69.93 | -60.79 | -52.79 |
| typical+gain1.0dB | -69.93 | -60.71 | -52.71 |
| typical+gain2.0dB | -69.94 | -61.50 | -53.50 |

## Quality gate: INVALID rate (expected ~0 for clean/shift/flatten, ~1 for detune/open/short; 'floor' rejects whole profiles whose floor is within 8 dB of τ)
| case | ideal | good | typical | noisy | very_noisy | typical_jitter | typical+gain0.5dB | typical+gain1.0dB | typical+gain2.0dB |
|---|---|---|---|---|---|---|---|---|---|
| clean | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.963 |
| shift-2MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.969 |
| shift+2MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.963 |
| shift-5MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.969 |
| shift+5MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.963 |
| shift-10MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.969 |
| shift+10MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.756 | 0.963 |
| shift-20MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.081 | 0.769 | 0.969 |
| shift+20MHz | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.075 | 0.750 | 0.963 |
| flatten_notch | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.087 | 0.775 | 0.969 |
| detune-200MHz | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.806 | 0.969 |
| detune+200MHz | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.956 |
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
| typical | one_open | 1.000 | 1.000 | 0.013 | 0.000 | 1.000 | 0.069 | 0.000 |
| typical | one_short | 1.000 | 1.000 | 0.013 | 0.000 | 1.000 | 0.069 | 0.000 |
| noisy | clean | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 1.000 |
| very_noisy | clean | 1.000 | 0.000 | 0.031 | 0.000 | 0.000 | 0.000 | 1.000 |
| typical_jitter | clean | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical+gain0.5dB | clean | 0.081 | 0.000 | 0.081 | 0.000 | 0.000 | 0.000 | 0.000 |
| typical+gain1.0dB | clean | 0.756 | 0.000 | 0.744 | 0.000 | 0.287 | 0.000 | 0.000 |
| typical+gain2.0dB | clean | 0.963 | 0.631 | 0.900 | 0.000 | 0.900 | 0.006 | 0.000 |

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
| flatten_notch | 0.000 | 0.000 | 0.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.000 |
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
| M5.C3 ring-mean | full | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.772 | -52.807 | -52.755 | 0.070 |
| M5.C3 ring-mean | full | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.757 | -52.758 | -52.757 | 0.069 |
| M5.C3 ring-mean | full | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.716 | -52.736 | -52.706 | 0.074 |
| M5.C3 ring-mean | full | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.778 | -52.780 | -52.776 | 0.068 |
| M5.C3 ring-mean | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.069 | 1.000 | 1.000 | -52.760 | -52.866 | -52.706 | 0.140 |
| M5.C3 ring-mean | full | typical+gain1.0dB | 1.000 | 0.767 | 0.106 | 0.686 | 1.000 | 0.958 | -52.694 | -52.718 | -52.681 | 0.253 |
| M5.C3 ring-mean | full | typical+gain2.0dB | 1.000 | 0.000 | 0.500 | 0.956 | 1.000 | 0.000 | -53.073 | -53.190 | -52.974 | 0.486 |
| M5.C3 ring-mean | full | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.793 | -52.796 | -52.792 | 0.068 |
| M5.C3 ring-mean | full | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -51.005 | -51.021 | -50.996 | 0.137 |
| M5.C3 ring-mean | gain_invariant | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.772 | -52.807 | -52.755 | 0.070 |
| M5.C3 ring-mean | gain_invariant | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.757 | -52.758 | -52.757 | 0.069 |
| M5.C3 ring-mean | gain_invariant | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.716 | -52.736 | -52.706 | 0.074 |
| M5.C3 ring-mean | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.778 | -52.780 | -52.776 | 0.068 |
| M5.C3 ring-mean | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.760 | -52.866 | -52.706 | 0.140 |
| M5.C3 ring-mean | gain_invariant | typical+gain1.0dB | 0.933 | 0.867 | 0.092 | 0.000 | 0.994 | 0.987 | -52.694 | -52.718 | -52.681 | 0.253 |
| M5.C3 ring-mean | gain_invariant | typical+gain2.0dB | 0.533 | 0.728 | 0.278 | 0.000 | 0.807 | 0.929 | -53.073 | -53.190 | -52.974 | 0.486 |
| M5.C3 ring-mean | gain_invariant | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.793 | -52.796 | -52.792 | 0.068 |
| M5.C3 ring-mean | gain_invariant | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -51.005 | -51.021 | -50.996 | 0.137 |
| M5.C3 vote(6 views) | full | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.711 | -52.917 | -52.418 | 0.220 |
| M5.C3 vote(6 views) | full | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.707 | -52.838 | -52.514 | 0.224 |
| M5.C3 vote(6 views) | full | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.616 | -52.815 | -52.410 | 0.258 |
| M5.C3 vote(6 views) | full | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.690 | -52.796 | -52.555 | 0.224 |
| M5.C3 vote(6 views) | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.069 | 1.000 | 1.000 | -52.743 | -52.810 | -52.628 | 0.314 |
| M5.C3 vote(6 views) | full | typical+gain1.0dB | 0.981 | 0.722 | 0.106 | 0.686 | 1.000 | 0.884 | -52.737 | -52.899 | -52.691 | 0.488 |
| M5.C3 vote(6 views) | full | typical+gain2.0dB | 1.000 | 0.222 | 0.458 | 0.956 | 1.000 | 0.571 | -53.388 | -53.529 | -53.258 | 1.192 |
| M5.C3 vote(6 views) | full | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.663 | -52.783 | -52.421 | 0.231 |
| M5.C3 vote(6 views) | full | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -50.899 | -50.951 | -50.800 | 0.331 |
| M5.C3 vote(6 views) | gain_invariant | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.711 | -52.917 | -52.418 | 0.220 |
| M5.C3 vote(6 views) | gain_invariant | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.707 | -52.838 | -52.514 | 0.224 |
| M5.C3 vote(6 views) | gain_invariant | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -52.616 | -52.815 | -52.410 | 0.258 |
| M5.C3 vote(6 views) | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.690 | -52.796 | -52.555 | 0.224 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.743 | -52.810 | -52.628 | 0.314 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain1.0dB | 0.909 | 0.874 | 0.081 | 0.000 | 0.976 | 0.963 | -52.737 | -52.899 | -52.691 | 0.488 |
| M5.C3 vote(6 views) | gain_invariant | typical+gain2.0dB | 0.470 | 0.837 | 0.192 | 0.000 | 0.640 | 0.950 | -53.388 | -53.529 | -53.258 | 1.192 |
| M5.C3 vote(6 views) | gain_invariant | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -52.663 | -52.783 | -52.421 | 0.231 |
| M5.C3 vote(6 views) | gain_invariant | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -50.899 | -50.951 | -50.800 | 0.331 |
| M5.R31 | full | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.216 | -15.332 | -15.159 | 0.068 |
| M5.R31 | full | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.220 | -15.333 | -15.164 | 0.068 |
| M5.R31 | full | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -15.189 | -15.296 | -15.136 | 0.064 |
| M5.R31 | full | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.218 | -15.328 | -15.163 | 0.068 |
| M5.R31 | full | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.069 | 1.000 | 1.000 | -15.227 | -15.339 | -15.171 | 0.068 |
| M5.R31 | full | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.686 | 1.000 | 1.000 | -15.207 | -15.333 | -15.143 | 0.065 |
| M5.R31 | full | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.956 | 1.000 | 1.000 | -15.216 | -15.342 | -15.152 | 0.064 |
| M5.R31 | full | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.221 | -15.335 | -15.164 | 0.068 |
| M5.R31 | full | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -13.673 | -13.753 | -13.634 | 0.137 |
| M5.R31 | gain_invariant | good | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.216 | -15.332 | -15.159 | 0.068 |
| M5.R31 | gain_invariant | ideal | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.220 | -15.333 | -15.164 | 0.068 |
| M5.R31 | gain_invariant | noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -15.189 | -15.296 | -15.136 | 0.064 |
| M5.R31 | gain_invariant | typical | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.218 | -15.328 | -15.163 | 0.068 |
| M5.R31 | gain_invariant | typical+gain0.5dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.227 | -15.339 | -15.171 | 0.068 |
| M5.R31 | gain_invariant | typical+gain1.0dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.207 | -15.333 | -15.143 | 0.065 |
| M5.R31 | gain_invariant | typical+gain2.0dB | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.216 | -15.342 | -15.152 | 0.064 |
| M5.R31 | gain_invariant | typical_jitter | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 1.000 | -15.221 | -15.335 | -15.164 | 0.068 |
| M5.R31 | gain_invariant | very_noisy | n/a | n/a | n/a | 1.000 | n/a | n/a | -13.673 | -13.753 | -13.634 | 0.137 |

## `binary` at `typical` (top 12 by balanced accuracy + M0)
CV: LODO+LOSO-within-class (9 folds), noise-robustness-only.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| M9 | LDA | 1 | 1 | 1 | 0.00324 | 1 | 0 |  |
| M9 | LR | 1 | 1 | 1 | 0 | 1 | 0 |  |
| COMB | LDA | 1 | 1 | 1 | 0.00463 | 1 | 0 | chosen M5.C3+M6.A[3.40]+M5.C2×7; M5.C3+M6.A[3.40]+M6.A[3.55]×1; M5.C3+M6.A[3.40]+M6.A[3.50]×1 |
| COMB | LR | 1 | 1 | 1 | 0 | 1 | 0 | chosen M5.C3+M6.A[3.40]+M5.C2×7; M5.C3+M6.A[3.40]+M6.A[3.55]×1; M5.C3+M6.A[3.40]+M6.A[3.50]×1 |
| M6 | RBF | 1 | 1 | 1 | 0.00231 | 1 | 0 |  |
| COMB | ORD | 1 | 1 | 1 | 0 | 1 | 0 | chosen M5.C3+M6.A[3.40]+M5.C2×7; M5.C3+M6.A[3.40]+M6.A[3.55]×1; M5.C3+M6.A[3.40]+M6.A[3.50]×1 |
| COMB | kNN | 1 | 1 | 1 | 0 | 1 | 0 | chosen M5.C3+M6.A[3.40]+M5.C2×7; M5.C3+M6.A[3.40]+M6.A[3.55]×1; M5.C3+M6.A[3.40]+M6.A[3.50]×1 |
| COMB | RBF | 1 | 1 | 1 | 0 | 1 | 0 | chosen M5.C3+M6.A[3.40]+M5.C2×7; M5.C3+M6.A[3.40]+M6.A[3.55]×1; M5.C3+M6.A[3.40]+M6.A[3.50]×1 |
| COMB | LSVM | 1 | 1 | 1 | 0 | 1 | 0 | chosen M5.C3+M6.A[3.40]+M5.C2×7; M5.C3+M6.A[3.40]+M6.A[3.55]×1; M5.C3+M6.A[3.40]+M6.A[3.50]×1 |
| M9 | ORD | 1 | 1 | 1 | 0 | 1 | 0 |  |
| M5.C3[nested] | LDA | 1 | 1 | 1 | 0.0134 | 1 | 0 | windows 3.40-3.50×6, 3.45-3.55×2, 3.40-3.60×1 |
| M5.C3[nested] | LSVM | 1 | 1 | 1 | 0.0116 | 1 | 0 | windows 3.40-3.50×6, 3.45-3.55×2, 3.40-3.60×1 |
| M0 | ORD | 0.585 | 0.585 | 0.585 | 0.891 | 0.677 | 0 |  |
| M0 | THR | 0.585 | 0.585 | 0.585 | 0.883 | 0.65 | 0 |  |
| M0 | RBF | 0.585 | 0.585 | 0.585 | 1 | n/a | 0 |  |
| M0 | LR | 0.585 | 0.585 | 0.585 | 0.853 | 0.665 | 0 |  |
| M0 | LDA | 0.585 | 0.585 | 0.585 | 0.891 | 0.669 | 0 |  |
| M0 | LSVM | 0.585 | 0.585 | 0.585 | 0.893 | 0.673 | 0 |  |
| M0 | kNN | 0.554 | 0.554 | 0.554 | 0.973 | 0.619 | 0 |  |

## `three_merged` at `typical` (top 12 by balanced accuracy + M0) - UNVERIFIED AGAINST MESH NOISE
CV: LODO+LOSO-within-class (6 folds), noise-robustness-only.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| M9 | LDA | 0.998 | 0.998 | 0.998 | 0.0806 | 0.661 | 0 |  |
| M9 | ORD | 0.997 | 0.997 | 0.997 | 0.00231 | 1 | 0 |  |
| M6 | LDA | 0.982 | 0.982 | 0.982 | 0.0537 | 0.914 | 0 |  |
| M6 | ORD | 0.975 | 0.975 | 0.974 | 0.0667 | 0.986 | 0 |  |
| M9 | RBF | 0.975 | 0.975 | 0.975 | 0.00602 | 0.986 | 0 |  |
| M9 | LR | 0.97 | 0.97 | 0.97 | 0.00324 | 0.995 | 0 |  |
| M5 | kNN | 0.946 | 0.946 | 0.946 | 0.0264 | 0.957 | 0 |  |
| M5 | RBF | 0.946 | 0.946 | 0.946 | 0.013 | 0.944 | 0 |  |
| M5 | LDA | 0.945 | 0.945 | 0.945 | 0.0338 | 0.956 | 0 |  |
| M9 | kNN | 0.941 | 0.941 | 0.941 | 0.0616 | 0.95 | 0 |  |
| M6 | RBF | 0.934 | 0.934 | 0.934 | 0.075 | 0.919 | 0 |  |
| M6 | LR | 0.924 | 0.924 | 0.923 | 0.0528 | 0.928 | 0 |  |
| M0 | LDA | 0.399 | 0.399 | 0.387 | 0.998 | 0.333 | 0 |  |
| M0 | ORD | 0.398 | 0.398 | 0.377 | 0.998 | n/a | 0 |  |
| M0 | LSVM | 0.396 | 0.396 | 0.35 | 1 | n/a | 0 |  |
| M0 | LR | 0.396 | 0.396 | 0.385 | 0.995 | 0.333 | 0 |  |
| M0 | RBF | 0.392 | 0.392 | 0.373 | 1 | n/a | 0 |  |
| M0 | kNN | 0.37 | 0.37 | 0.362 | 1 | n/a | 0 |  |

## `three` at `typical` (top 12 by balanced accuracy + M0) - UNVERIFIED AGAINST MESH NOISE
CV: LODO (3 folds), noise-robustness-only.
| feature_set | model | balanced_accuracy | accuracy | macro_f1 | reject_rate | bal_acc_on_accepted | gate_invalid_rate | info |
|---|---|---|---|---|---|---|---|---|
| M9 | LDA | 1 | 1 | 1 | 0.0176 | 0.887 | 0 |  |
| M9 | ORD | 1 | 1 | 1 | 0 | 1 | 0 |  |
| M9 | RBF | 0.994 | 0.994 | 0.994 | 0.0185 | 0.983 | 0 |  |
| M6 | ORD | 0.991 | 0.991 | 0.991 | 0.0556 | 0.966 | 0 |  |
| M9 | LR | 0.981 | 0.981 | 0.981 | 0.0037 | 0.993 | 0 |  |
| M6 | LDA | 0.976 | 0.976 | 0.976 | 0.0481 | 0.921 | 0 |  |
| M5 | RBF | 0.965 | 0.965 | 0.965 | 0.0194 | 0.978 | 0 |  |
| M6 | LR | 0.959 | 0.959 | 0.959 | 0.0454 | 0.9 | 0 |  |
| M5 | kNN | 0.958 | 0.958 | 0.958 | 0.0611 | 0.983 | 0 |  |
| M5 | LDA | 0.952 | 0.952 | 0.952 | 0.0528 | 0.82 | 0 |  |
| COMB | LDA | 0.94 | 0.94 | 0.939 | 0.0574 | 0.825 | 0 | chosen M5.C2+M6.A[3.40]+M5.C3×1; M5.C2+M6.A[3.40]+M5.C×1; M5.C2+M6.A[3.40]+M5.C1×1 |
| M5 | LR | 0.936 | 0.936 | 0.937 | 0.0426 | 0.976 | 0 |  |
| M0 | LDA | 0.396 | 0.396 | 0.364 | 0.998 | n/a | 0 |  |
| M0 | LR | 0.396 | 0.396 | 0.359 | 0.996 | n/a | 0 |  |
| M0 | ORD | 0.392 | 0.392 | 0.367 | 0.999 | n/a | 0 |  |
| M0 | LSVM | 0.392 | 0.392 | 0.313 | 0.999 | n/a | 0 |  |
| M0 | RBF | 0.387 | 0.387 | 0.374 | 1 | n/a | 0 |  |
| M0 | kNN | 0.369 | 0.369 | 0.364 | 0.991 | 0.5 | 0 |  |

## Per-port amplitude (gain) errors, binary, per view (balanced accuracy)
| feature_set | model | no gain error | typical+gain0.5dB | typical+gain1.0dB | typical+gain2.0dB |
|---|---|---|---|---|---|
| COMB | LR | 1.000 | 0.993 | 0.934 | 0.889 |
| M0 | LR | 0.585 | 0.537 | 0.526 | 0.417 |
| M0 | THR | 0.585 | 0.535 | 0.530 | 0.583 |
| M5.C3 | LR | 0.974 | 0.929 | 0.871 | 0.583 |
| M5.C3 | THR | 0.978 | 0.943 | 0.881 | 0.667 |
| M5.C3[nested] | LR | 1.000 | 0.958 | 0.907 | 0.660 |
| M5.C3[nested] | THR | 1.000 | 0.945 | 0.912 | 0.778 |
| M9 | LR | 1.000 | 1.000 | 1.000 | 1.000 |

## Binary thresholds (Normal | AD), dB, per profile
τ = class-balanced (equal priors) error minimiser; τ_screen uses P(Normal) = 0.8; CI = bootstrap over simulations (within class), views and draws (1000×). Margin m = max(posterior margin at p* = 0.7, Φ⁻¹(p*)·σ_ref); σ_ref = within-simulation SD of one view (one measurement for R31) (between-mesh SD not yet measured). M5.C3_raw = without floor subtraction. Sensitivity/specificity here are resubstitution.
| feature | profile | tau_dB | tau_CI_lo | tau_CI_hi | tau_screen_dB | margin_dB | sd_ref_dB | mu_Normal_dB | mu_AD_dB | sensitivity | specificity | uncertain_fraction |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M5.C3 | good | -52.86 | -53.01 | -52.68 | -52.86 | 0.2365 | 0.4511 | -51.82 | -53.8 | 0.9944 | 1 | 0.03264 |
| M5.C3 | ideal | -52.77 | -53.04 | -52.76 | -52.77 | 0.2387 | 0.4552 | -51.84 | -53.81 | 1 | 1 | 0.01215 |
| M5.C3 | noisy | -52.66 | -52.86 | -52.56 | -52.73 | 0.267 | 0.5091 | -51.78 | -53.75 | 0.9931 | 0.9917 | 0.05035 |
| M5.C3 | typical | -52.79 | -53.01 | -52.73 | -52.79 | 0.2367 | 0.4513 | -51.83 | -53.8 | 0.9986 | 1 | 0.02326 |
| M5.C3 | typical+gain0.5dB | -52.69 | -52.91 | -52.65 | -52.98 | 0.3219 | 0.6138 | -51.83 | -53.79 | 0.9644 | 0.9458 | 0.1229 |
| M5.C3 | typical+gain1.0dB | -52.74 | -52.82 | -52.59 | -53.66 | 0.496 | 0.9459 | -51.85 | -53.8 | 0.8579 | 0.8417 | 0.2361 |
| M5.C3 | typical+gain2.0dB | -53.29 | -53.51 | -52.42 | -55.1 | 1.313 | 1.683 | -51.96 | -53.75 | 0.6097 | 0.8056 | 0.5038 |
| M5.C3 | typical_jitter | -52.78 | -52.86 | -52.63 | -52.78 | 0.2362 | 0.4505 | -51.82 | -53.8 | 0.9986 | 1 | 0.01806 |
| M5.C3 | very_noisy | -50.89 | -50.96 | -50.78 | -51.22 | 0.3403 | 0.6489 | -50.33 | -51.64 | 0.8769 | 0.8472 | 0.2486 |
| M5.C3[k3] | good | -48.73 | -49.18 | -48.69 | -48.73 | 0.2572 | 0.4905 | -47.55 | -50.06 | 1 | 1 | 0.005903 |
| M5.C3[k3] | ideal | -48.77 | -49.2 | -48.76 | -48.77 | 0.26 | 0.4958 | -47.58 | -50.07 | 1 | 1 | 0.004861 |
| M5.C3[k3] | noisy | -48.73 | -48.86 | -48.47 | -48.73 | 0.2958 | 0.5641 | -47.53 | -50.02 | 0.9958 | 1 | 0.02882 |
| M5.C3[k3] | typical | -48.72 | -49.17 | -48.71 | -48.72 | 0.2604 | 0.4965 | -47.57 | -50.06 | 1 | 1 | 0.007292 |
| M5.C3[k3] | typical+gain0.5dB | -48.79 | -48.98 | -48.61 | -48.94 | 0.3397 | 0.6478 | -47.57 | -50.05 | 0.9741 | 0.9861 | 0.075 |
| M5.C3[k3] | typical+gain1.0dB | -48.83 | -48.97 | -48.43 | -49.48 | 0.5073 | 0.9673 | -47.58 | -50.05 | 0.8894 | 0.8958 | 0.1979 |
| M5.C3[k3] | typical+gain2.0dB | -48.91 | -49.3 | -48.6 | -50.27 | 1.025 | 1.69 | -47.7 | -50.01 | 0.7269 | 0.7806 | 0.3611 |
| M5.C3[k3] | typical_jitter | -48.67 | -49.1 | -48.64 | -48.67 | 0.2602 | 0.4962 | -47.56 | -50.06 | 1 | 1 | 0.002778 |
| M5.C3[k3] | very_noisy | -47.85 | -47.99 | -47.73 | -48.4 | 0.4699 | 0.8961 | -46.93 | -49.02 | 0.9051 | 0.8958 | 0.2198 |
| M5.C3_raw | good | -52.85 | -53 | -52.67 | -52.85 | 0.236 | 0.45 | -51.81 | -53.79 | 0.9944 | 1 | 0.03264 |
| M5.C3_raw | ideal | -52.77 | -53.04 | -52.76 | -52.77 | 0.2386 | 0.4551 | -51.84 | -53.81 | 1 | 1 | 0.01215 |
| M5.C3_raw | noisy | -51.9 | -52.07 | -51.86 | -52 | 0.2178 | 0.4154 | -51.17 | -52.83 | 0.9972 | 0.9875 | 0.0434 |
| M5.C3_raw | typical | -52.69 | -52.92 | -52.64 | -52.76 | 0.2312 | 0.441 | -51.76 | -53.7 | 0.9995 | 0.9986 | 0.02292 |
| M5.C3_raw | typical+gain0.5dB | -52.59 | -52.82 | -52.57 | -52.9 | 0.3146 | 0.6 | -51.77 | -53.69 | 0.9685 | 0.9417 | 0.1174 |
| M5.C3_raw | typical+gain1.0dB | -52.66 | -52.73 | -52.51 | -53.56 | 0.485 | 0.9248 | -51.78 | -53.69 | 0.8565 | 0.8417 | 0.2351 |
| M5.C3_raw | typical+gain2.0dB | -53.19 | -53.43 | -52.38 | -54.96 | 1.289 | 1.645 | -51.89 | -53.64 | 0.6116 | 0.8028 | 0.5062 |
| M5.C3_raw | typical_jitter | -52.69 | -52.78 | -52.56 | -52.69 | 0.2308 | 0.44 | -51.75 | -53.69 | 0.9986 | 1 | 0.01771 |
| M5.C3_raw | very_noisy | -48.1 | -48.12 | -47.99 | -48.3 | 0.1671 | 0.3187 | -47.78 | -48.46 | 0.8741 | 0.85 | 0.2306 |
| M5.R31 | good | -15.16 | -15.49 | -15.16 | -15.49 | 0.05492 | 0.01072 | -14.48 | -16.18 | 1 | 1 | 0 |
| M5.R31 | ideal | -15.16 | -15.49 | -15.16 | -15.5 | 0.05779 | 0.004283 | -14.48 | -16.18 | 1 | 1 | 0 |
| M5.R31 | noisy | -15.09 | -15.45 | -15.09 | -15.31 | 0.05149 | 0.09678 | -14.47 | -16.17 | 1 | 1 | 0 |
| M5.R31 | typical | -15.17 | -15.48 | -15.16 | -15.48 | 0.05474 | 0.03205 | -14.48 | -16.18 | 1 | 1 | 0 |
| M5.R31 | typical+gain0.5dB | -15.16 | -15.48 | -15.15 | -15.47 | 0.05772 | 0.03017 | -14.48 | -16.19 | 1 | 1 | 0 |
| M5.R31 | typical+gain1.0dB | -15.15 | -15.49 | -15.14 | -15.45 | 0.05735 | 0.03049 | -14.48 | -16.19 | 1 | 1 | 0 |
| M5.R31 | typical+gain2.0dB | -15.16 | -15.49 | -15.15 | -15.46 | 0.05749 | 0.0334 | -14.48 | -16.19 | 1 | 1 | 0 |
| M5.R31 | typical_jitter | -15.16 | -15.49 | -15.16 | -15.47 | 0.05448 | 0.03167 | -14.48 | -16.18 | 1 | 1 | 0 |
| M5.R31 | very_noisy | -13.63 | -13.77 | -13.55 | -13.64 | 0.1356 | 0.2585 | -13.16 | -14.21 | 0.9694 | 0.9833 | 0.09167 |

### τ drift between profiles (dB)
| feature | tau_typical | drift_ideal..typical_jitter | tau_noisy - tau_typical | tau_very_noisy - tau_typical | max |tau(gain) - tau_typical| |
|---|---|---|---|---|---|
| M5.C3 | -52.785 | 0.087 | 0.123 | 1.891 | 0.502 |
| M5.C3[k3] | -48.721 | 0.100 | -0.005 | 0.873 | 0.190 |
| M5.C3_raw | -52.687 | 0.161 | 0.790 | 4.588 | 0.502 |
| M5.R31 | -15.171 | 0.012 | 0.077 | 1.537 | 0.018 |

### CV sensitivity / specificity of the fold-fitted threshold (THR, per view)
| profile | feature_set | cv_sensitivity | cv_specificity | fold_tau_dB_min | fold_tau_dB_max |
|---|---|---|---|---|---|
| ideal | M0 | 0.4148 | 0.7361 | -2.501 | -2.44 |
| ideal | M5.C3 | 0.9972 | 0.9602 | -52.83 | -52.5 |
| ideal | M5.C3[k3] | 1 | 0.9926 | -48.84 | -48.35 |
| ideal | M5.C3[nested] | 1 | 1 | -48.52 | -48.05 |
| good | M0 | 0.5741 | 0.5944 | -2.61 | -2.467 |
| good | M5.C3 | 0.9907 | 0.9361 | -52.91 | -52.4 |
| good | M5.C3[k3] | 0.9926 | 0.9685 | -48.93 | -48.27 |
| good | M5.C3[nested] | 0.9963 | 0.9926 | -48.4 | -48.05 |
| typical | M0 | 0.6083 | 0.562 | -2.629 | -2.537 |
| typical | M5.C3 | 0.9963 | 0.9593 | -52.79 | -52.55 |
| typical | M5.C3[k3] | 1 | 0.9815 | -48.81 | -48.39 |
| typical | M5.C3[nested] | 0.9991 | 1 | -48.62 | -48.01 |
| noisy | M0 | n/a | n/a | -2.667 | -2.592 |
| noisy | M5.C3 | n/a | n/a | -52.81 | -52.41 |
| noisy | M5.C3[k3] | n/a | n/a | -48.69 | -48.36 |
| noisy | M5.C3[nested] | n/a | n/a | -48.5 | -48.31 |
| very_noisy | M0 | n/a | n/a | -2.588 | -2.553 |
| very_noisy | M5.C3 | n/a | n/a | -50.95 | -50.8 |
| very_noisy | M5.C3[k3] | n/a | n/a | -47.87 | -47.71 |
| very_noisy | M5.C3[nested] | n/a | n/a | -48.92 | -47.73 |
| typical_jitter | M0 | 0.5657 | 0.5704 | -2.7 | -2.479 |
| typical_jitter | M5.C3 | 0.9991 | 0.9787 | -52.78 | -52.41 |
| typical_jitter | M5.C3[k3] | 1 | 0.9972 | -48.73 | -48.29 |
| typical_jitter | M5.C3[nested] | 1 | 1 | -48.41 | -48.07 |
| typical+gain0.5dB | M0 | 0.6796 | 0.3909 | -3.233 | -2.233 |
| typical+gain0.5dB | M5.C3 | 0.9511 | 0.9345 | -52.81 | -52.63 |
| typical+gain0.5dB | M5.C3[nested] | 0.976 | 0.9147 | -48.89 | -48.21 |
| typical+gain1.0dB | M0 | 0.2987 | 0.7611 | -2.207 | -1.736 |
| typical+gain1.0dB | M5.C3 | 0.9686 | 0.7944 | -52.9 | -52.69 |
| typical+gain1.0dB | M5.C3[nested] | 0.9843 | 0.8389 | -50.1 | -48.83 |
| typical+gain2.0dB | M0 | 0.25 | 0.9167 | -1.359 | -1.336 |
| typical+gain2.0dB | M5.C3 | 0.9167 | 0.4167 | -53.53 | -53.26 |
| typical+gain2.0dB | M5.C3[nested] | 1 | 0.5556 | -50.64 | -49.01 |
