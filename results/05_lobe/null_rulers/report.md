# Null rulers, pre-registered evaluation (code 15d17bb; POST HOC with respect to Test_B and RightOnly)

Rotated nulls in the manifest: Null_rot07, Null_rot19, Null_rot31, Null_rot43. Only 'all nulls' is the ruler; the other two variants show the dependence on Null_rot19 and are not adopted.

## P. Path classes: common-mode or scattered (descriptive; criterion in the script docstring)
| band | pair | k=1 (neighbour) | k=2 (second-neighbour) | k=3 (opposite) |
|---|---|---|---|---|
| 3.2-4.2 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | scattered | scattered | scattered |
| 3.2-4.2 GHz | Null_rot07 - Healthy_sliced_new | scattered | scattered | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot19 | scattered | scattered | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot31 | scattered | scattered | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot43 | common-mode | scattered | common-mode |
| 3.2-4.2 GHz | Null_rot19 - Healthy_sliced_new | common-mode | scattered | common-mode |
| 3.2-4.2 GHz | Null_rot19 - Null_rot31 | scattered | scattered | scattered |
| 3.2-4.2 GHz | Null_rot19 - Null_rot43 | scattered | scattered | common-mode |
| 3.2-4.2 GHz | Null_rot31 - Healthy_sliced_new | scattered | scattered | scattered |
| 3.2-4.2 GHz | Null_rot31 - Null_rot43 | scattered | scattered | common-mode |
| 3.2-4.2 GHz | Null_rot43 - Healthy_sliced_new | scattered | scattered | common-mode |
| 3.2-4.2 GHz | twin Healthy 6->7 (b - a) | scattered | scattered | common-mode |
| 3.2-4.2 GHz | twin Mild 5->6 (b - a) | scattered | scattered | scattered |
| 3.2-4.2 GHz | twin Moderate 5->6 (b - a) | scattered | scattered | scattered |
| 3.2-4.2 GHz | twin Severe 5->6 (b - a) | scattered | scattered | scattered |
| 3.30-3.65 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | scattered | scattered | scattered |
| 3.30-3.65 GHz | Null_rot07 - Healthy_sliced_new | scattered | scattered | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot19 | scattered | common-mode | common-mode |
| 3.30-3.65 GHz | Null_rot07 - Null_rot31 | scattered | scattered | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot43 | common-mode | scattered | common-mode |
| 3.30-3.65 GHz | Null_rot19 - Healthy_sliced_new | scattered | scattered | common-mode |
| 3.30-3.65 GHz | Null_rot19 - Null_rot31 | scattered | scattered | scattered |
| 3.30-3.65 GHz | Null_rot19 - Null_rot43 | scattered | scattered | scattered |
| 3.30-3.65 GHz | Null_rot31 - Healthy_sliced_new | scattered | scattered | common-mode |
| 3.30-3.65 GHz | Null_rot31 - Null_rot43 | common-mode | scattered | common-mode |
| 3.30-3.65 GHz | Null_rot43 - Healthy_sliced_new | common-mode | scattered | common-mode |
| 3.30-3.65 GHz | twin Healthy 6->7 (b - a) | scattered | scattered | common-mode |
| 3.30-3.65 GHz | twin Mild 5->6 (b - a) | common-mode | scattered | scattered |
| 3.30-3.65 GHz | twin Moderate 5->6 (b - a) | scattered | scattered | scattered |
| 3.30-3.65 GHz | twin Severe 5->6 (b - a) | scattered | scattered | scattered |

| band | pair | class | n paths | H6 level (dB) | mean (dB) | SD about mean (dB) | min | max | same sign as mean | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.30-3.65 GHz | Null_rot07 - Healthy_sliced_new | k=1 (neighbour) | 6 | -35.358 | -0.015 | 0.143 | -0.191 | 0.210 | 4/6 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -54.084 | 0.054 | 0.120 | -0.102 | 0.202 | 3/6 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Healthy_sliced_new | k=3 (opposite) | 3 | -47.943 | 0.031 | 0.052 | -0.042 | 0.077 | 2/3 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Healthy_sliced_new | k=1 (neighbour) | 6 | -35.358 | 0.219 | 0.118 | 0.077 | 0.383 | 6/6 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -54.084 | -0.309 | 0.225 | -0.540 | 0.121 | 5/6 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Healthy_sliced_new | k=3 (opposite) | 3 | -47.943 | 0.313 | 0.065 | 0.255 | 0.404 | 3/3 | common-mode |
| 3.30-3.65 GHz | Null_rot31 - Healthy_sliced_new | k=1 (neighbour) | 6 | -35.358 | 0.041 | 0.112 | -0.123 | 0.230 | 3/6 | scattered |
| 3.30-3.65 GHz | Null_rot31 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -54.084 | 0.113 | 0.184 | -0.128 | 0.401 | 3/6 | scattered |
| 3.30-3.65 GHz | Null_rot31 - Healthy_sliced_new | k=3 (opposite) | 3 | -47.943 | 0.206 | 0.071 | 0.105 | 0.262 | 3/3 | common-mode |
| 3.30-3.65 GHz | Null_rot43 - Healthy_sliced_new | k=1 (neighbour) | 6 | -35.358 | 0.228 | 0.111 | 0.073 | 0.429 | 6/6 | common-mode |
| 3.30-3.65 GHz | Null_rot43 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -54.084 | -0.028 | 0.192 | -0.220 | 0.357 | 4/6 | scattered |
| 3.30-3.65 GHz | Null_rot43 - Healthy_sliced_new | k=3 (opposite) | 3 | -47.943 | 0.401 | 0.027 | 0.364 | 0.426 | 3/3 | common-mode |
| 3.30-3.65 GHz | Null_rot07 - Null_rot19 | k=1 (neighbour) | 6 | -35.358 | -0.234 | 0.158 | -0.442 | 0.035 | 5/6 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot19 | k=2 (second-neighbour) | 6 | -54.084 | 0.362 | 0.167 | 0.062 | 0.591 | 6/6 | common-mode |
| 3.30-3.65 GHz | Null_rot07 - Null_rot19 | k=3 (opposite) | 3 | -47.943 | -0.282 | 0.116 | -0.446 | -0.197 | 3/3 | common-mode |
| 3.30-3.65 GHz | Null_rot07 - Null_rot31 | k=1 (neighbour) | 6 | -35.358 | -0.055 | 0.053 | -0.140 | 0.031 | 5/6 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot31 | k=2 (second-neighbour) | 6 | -54.084 | -0.059 | 0.258 | -0.502 | 0.204 | 3/6 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot31 | k=3 (opposite) | 3 | -47.943 | -0.175 | 0.101 | -0.293 | -0.047 | 3/3 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot43 | k=1 (neighbour) | 6 | -35.358 | -0.243 | 0.098 | -0.359 | -0.083 | 6/6 | common-mode |
| 3.30-3.65 GHz | Null_rot07 - Null_rot43 | k=2 (second-neighbour) | 6 | -54.084 | 0.082 | 0.297 | -0.459 | 0.408 | 4/6 | scattered |
| 3.30-3.65 GHz | Null_rot07 - Null_rot43 | k=3 (opposite) | 3 | -47.943 | -0.370 | 0.075 | -0.469 | -0.287 | 3/3 | common-mode |
| 3.30-3.65 GHz | Null_rot19 - Null_rot31 | k=1 (neighbour) | 6 | -35.358 | 0.178 | 0.138 | -0.004 | 0.393 | 5/6 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Null_rot31 | k=2 (second-neighbour) | 6 | -54.084 | -0.421 | 0.255 | -0.824 | -0.081 | 6/6 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Null_rot31 | k=3 (opposite) | 3 | -47.943 | 0.107 | 0.063 | 0.018 | 0.153 | 3/3 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Null_rot43 | k=1 (neighbour) | 6 | -35.358 | -0.009 | 0.115 | -0.175 | 0.133 | 3/6 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Null_rot43 | k=2 (second-neighbour) | 6 | -54.084 | -0.280 | 0.368 | -0.780 | 0.341 | 4/6 | scattered |
| 3.30-3.65 GHz | Null_rot19 - Null_rot43 | k=3 (opposite) | 3 | -47.943 | -0.088 | 0.055 | -0.158 | -0.022 | 3/3 | scattered |
| 3.30-3.65 GHz | Null_rot31 - Null_rot43 | k=1 (neighbour) | 6 | -35.358 | -0.187 | 0.092 | -0.272 | -0.020 | 6/6 | common-mode |
| 3.30-3.65 GHz | Null_rot31 - Null_rot43 | k=2 (second-neighbour) | 6 | -54.084 | 0.141 | 0.163 | -0.055 | 0.422 | 4/6 | scattered |
| 3.30-3.65 GHz | Null_rot31 - Null_rot43 | k=3 (opposite) | 3 | -47.943 | -0.195 | 0.085 | -0.308 | -0.102 | 3/3 | common-mode |
| 3.30-3.65 GHz | twin Healthy 6->7 (b - a) | k=1 (neighbour) | 6 | -35.358 | -0.085 | 0.046 | -0.137 | 0.000 | 5/6 | scattered |
| 3.30-3.65 GHz | twin Healthy 6->7 (b - a) | k=2 (second-neighbour) | 6 | -54.084 | 0.045 | 0.076 | -0.057 | 0.181 | 4/6 | scattered |
| 3.30-3.65 GHz | twin Healthy 6->7 (b - a) | k=3 (opposite) | 3 | -47.943 | 0.129 | 0.013 | 0.111 | 0.140 | 3/3 | common-mode |
| 3.30-3.65 GHz | twin Mild 5->6 (b - a) | k=1 (neighbour) | 6 | -35.358 | -0.074 | 0.028 | -0.113 | -0.035 | 6/6 | common-mode |
| 3.30-3.65 GHz | twin Mild 5->6 (b - a) | k=2 (second-neighbour) | 6 | -54.084 | 0.004 | 0.128 | -0.206 | 0.189 | 4/6 | scattered |
| 3.30-3.65 GHz | twin Mild 5->6 (b - a) | k=3 (opposite) | 3 | -47.943 | -0.039 | 0.088 | -0.139 | 0.075 | 2/3 | scattered |
| 3.30-3.65 GHz | twin Moderate 5->6 (b - a) | k=1 (neighbour) | 6 | -35.358 | -0.083 | 0.043 | -0.139 | -0.019 | 6/6 | scattered |
| 3.30-3.65 GHz | twin Moderate 5->6 (b - a) | k=2 (second-neighbour) | 6 | -54.084 | -0.027 | 0.037 | -0.071 | 0.023 | 4/6 | scattered |
| 3.30-3.65 GHz | twin Moderate 5->6 (b - a) | k=3 (opposite) | 3 | -47.943 | -0.008 | 0.051 | -0.080 | 0.032 | 1/3 | scattered |
| 3.30-3.65 GHz | twin Severe 5->6 (b - a) | k=1 (neighbour) | 6 | -35.358 | -0.081 | 0.073 | -0.190 | 0.025 | 4/6 | scattered |
| 3.30-3.65 GHz | twin Severe 5->6 (b - a) | k=2 (second-neighbour) | 6 | -54.084 | 0.120 | 0.066 | 0.044 | 0.240 | 6/6 | scattered |
| 3.30-3.65 GHz | twin Severe 5->6 (b - a) | k=3 (opposite) | 3 | -47.943 | -0.079 | 0.052 | -0.148 | -0.024 | 3/3 | scattered |
| 3.30-3.65 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | k=1 (neighbour) | 6 | -35.358 | -0.084 | 0.101 | -0.190 | 0.080 | 4/6 | scattered |
| 3.30-3.65 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | k=2 (second-neighbour) | 6 | -54.084 | -0.079 | 0.114 | -0.221 | 0.133 | 5/6 | scattered |
| 3.30-3.65 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | k=3 (opposite) | 3 | -47.943 | 0.040 | 0.200 | -0.213 | 0.277 | 2/3 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Healthy_sliced_new | k=1 (neighbour) | 6 | -36.859 | -0.015 | 0.110 | -0.147 | 0.139 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -57.422 | 0.055 | 0.137 | -0.192 | 0.208 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Healthy_sliced_new | k=3 (opposite) | 3 | -51.601 | 0.015 | 0.038 | -0.037 | 0.053 | 2/3 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Healthy_sliced_new | k=1 (neighbour) | 6 | -36.859 | 0.146 | 0.040 | 0.089 | 0.198 | 6/6 | common-mode |
| 3.2-4.2 GHz | Null_rot19 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -57.422 | -0.217 | 0.256 | -0.629 | 0.213 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Healthy_sliced_new | k=3 (opposite) | 3 | -51.601 | 0.251 | 0.101 | 0.142 | 0.385 | 3/3 | common-mode |
| 3.2-4.2 GHz | Null_rot31 - Healthy_sliced_new | k=1 (neighbour) | 6 | -36.859 | 0.025 | 0.075 | -0.050 | 0.169 | 3/6 | scattered |
| 3.2-4.2 GHz | Null_rot31 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -57.422 | 0.079 | 0.220 | -0.180 | 0.447 | 3/6 | scattered |
| 3.2-4.2 GHz | Null_rot31 - Healthy_sliced_new | k=3 (opposite) | 3 | -51.601 | 0.144 | 0.098 | 0.006 | 0.215 | 3/3 | scattered |
| 3.2-4.2 GHz | Null_rot43 - Healthy_sliced_new | k=1 (neighbour) | 6 | -36.859 | 0.157 | 0.106 | -0.028 | 0.241 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot43 - Healthy_sliced_new | k=2 (second-neighbour) | 6 | -57.422 | -0.015 | 0.189 | -0.179 | 0.367 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot43 - Healthy_sliced_new | k=3 (opposite) | 3 | -51.601 | 0.361 | 0.050 | 0.322 | 0.432 | 3/3 | common-mode |
| 3.2-4.2 GHz | Null_rot07 - Null_rot19 | k=1 (neighbour) | 6 | -36.859 | -0.161 | 0.118 | -0.262 | 0.032 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot19 | k=2 (second-neighbour) | 6 | -57.422 | 0.272 | 0.261 | -0.087 | 0.700 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot19 | k=3 (opposite) | 3 | -51.601 | -0.236 | 0.138 | -0.422 | -0.089 | 3/3 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot31 | k=1 (neighbour) | 6 | -36.859 | -0.040 | 0.092 | -0.213 | 0.100 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot31 | k=2 (second-neighbour) | 6 | -57.422 | -0.024 | 0.352 | -0.639 | 0.387 | 2/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot31 | k=3 (opposite) | 3 | -51.601 | -0.129 | 0.128 | -0.252 | 0.047 | 2/3 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot43 | k=1 (neighbour) | 6 | -36.859 | -0.172 | 0.076 | -0.288 | -0.097 | 6/6 | common-mode |
| 3.2-4.2 GHz | Null_rot07 - Null_rot43 | k=2 (second-neighbour) | 6 | -57.422 | 0.070 | 0.296 | -0.560 | 0.347 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot07 - Null_rot43 | k=3 (opposite) | 3 | -51.601 | -0.346 | 0.088 | -0.469 | -0.269 | 3/3 | common-mode |
| 3.2-4.2 GHz | Null_rot19 - Null_rot31 | k=1 (neighbour) | 6 | -36.859 | 0.121 | 0.094 | -0.004 | 0.231 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Null_rot31 | k=2 (second-neighbour) | 6 | -57.422 | -0.296 | 0.317 | -0.736 | 0.119 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Null_rot31 | k=3 (opposite) | 3 | -51.601 | 0.107 | 0.066 | 0.015 | 0.169 | 3/3 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Null_rot43 | k=1 (neighbour) | 6 | -36.859 | -0.011 | 0.097 | -0.145 | 0.117 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Null_rot43 | k=2 (second-neighbour) | 6 | -57.422 | -0.202 | 0.364 | -0.657 | 0.366 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot19 - Null_rot43 | k=3 (opposite) | 3 | -51.601 | -0.110 | 0.054 | -0.180 | -0.047 | 3/3 | common-mode |
| 3.2-4.2 GHz | Null_rot31 - Null_rot43 | k=1 (neighbour) | 6 | -36.859 | -0.132 | 0.124 | -0.258 | 0.094 | 5/6 | scattered |
| 3.2-4.2 GHz | Null_rot31 - Null_rot43 | k=2 (second-neighbour) | 6 | -57.422 | 0.094 | 0.200 | -0.250 | 0.392 | 4/6 | scattered |
| 3.2-4.2 GHz | Null_rot31 - Null_rot43 | k=3 (opposite) | 3 | -51.601 | -0.217 | 0.081 | -0.316 | -0.118 | 3/3 | common-mode |
| 3.2-4.2 GHz | twin Healthy 6->7 (b - a) | k=1 (neighbour) | 6 | -36.859 | -0.012 | 0.038 | -0.081 | 0.039 | 4/6 | scattered |
| 3.2-4.2 GHz | twin Healthy 6->7 (b - a) | k=2 (second-neighbour) | 6 | -57.422 | 0.048 | 0.096 | -0.088 | 0.174 | 4/6 | scattered |
| 3.2-4.2 GHz | twin Healthy 6->7 (b - a) | k=3 (opposite) | 3 | -51.601 | 0.124 | 0.002 | 0.121 | 0.126 | 3/3 | common-mode |
| 3.2-4.2 GHz | twin Mild 5->6 (b - a) | k=1 (neighbour) | 6 | -36.859 | -0.001 | 0.034 | -0.043 | 0.048 | 3/6 | scattered |
| 3.2-4.2 GHz | twin Mild 5->6 (b - a) | k=2 (second-neighbour) | 6 | -57.422 | 0.033 | 0.131 | -0.180 | 0.258 | 4/6 | scattered |
| 3.2-4.2 GHz | twin Mild 5->6 (b - a) | k=3 (opposite) | 3 | -51.601 | -0.035 | 0.091 | -0.146 | 0.077 | 2/3 | scattered |
| 3.2-4.2 GHz | twin Moderate 5->6 (b - a) | k=1 (neighbour) | 6 | -36.859 | -0.009 | 0.039 | -0.054 | 0.061 | 4/6 | scattered |
| 3.2-4.2 GHz | twin Moderate 5->6 (b - a) | k=2 (second-neighbour) | 6 | -57.422 | -0.009 | 0.047 | -0.079 | 0.055 | 2/6 | scattered |
| 3.2-4.2 GHz | twin Moderate 5->6 (b - a) | k=3 (opposite) | 3 | -51.601 | -0.013 | 0.052 | -0.085 | 0.032 | 1/3 | scattered |
| 3.2-4.2 GHz | twin Severe 5->6 (b - a) | k=1 (neighbour) | 6 | -36.859 | 0.001 | 0.049 | -0.094 | 0.066 | 3/6 | scattered |
| 3.2-4.2 GHz | twin Severe 5->6 (b - a) | k=2 (second-neighbour) | 6 | -57.422 | 0.109 | 0.055 | 0.044 | 0.176 | 6/6 | scattered |
| 3.2-4.2 GHz | twin Severe 5->6 (b - a) | k=3 (opposite) | 3 | -51.601 | -0.051 | 0.048 | -0.110 | 0.007 | 2/3 | scattered |
| 3.2-4.2 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | k=1 (neighbour) | 6 | -36.859 | 0.027 | 0.092 | -0.098 | 0.181 | 4/6 | scattered |
| 3.2-4.2 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | k=2 (second-neighbour) | 6 | -57.422 | -0.107 | 0.142 | -0.311 | 0.126 | 5/6 | scattered |
| 3.2-4.2 GHz | LeftOnly_test_c3 - mirrored RightOnly_test (pass 6 vs 5) | k=3 (opposite) | 3 | -51.601 | 0.040 | 0.199 | -0.219 | 0.266 | 2/3 | scattered |

## Rulers three ways
| ruler | all nulls | all nulls w/o rot19 | rot19 alone |
|---|---|---|---|
| yardstick R31 | 0.204 | 0.204 | 0.135 |
| yardstick R21 | 0.364 | 0.172 | 0.364 |
| yardstick R32 | 0.469 | 0.376 | 0.469 |
| yardstick index: front-back, all paths | 0.170 | 0.155 | 0.170 |
| yardstick index: front-back, neighbour paths | 0.223 | 0.223 | 0.068 |
| pattern-fit null contrast (deg) | 0.431 | 0.431 | 0.272 |
| healthy-twin ring mean (deg) | 1.111 | 1.111 | 0.302 |

(clean rulers of the 88 mirror statistics: rulers_three_ways.csv)

## Survival of the pre-registered items (verdict per variant; only 'all nulls' is the ruler)
| item | all nulls | all nulls w/o rot19 | rot19 alone |
|---|---|---|---|
| frozen labels >= 3x (A1), 30 lobe labels | 2/30 | 12/30 | 7/30 |
| staging labels (20): >= 3x / 2-3x / < 2x | sensitive: Healthy_sliced_new three_merged 2.53x, Severe_lobe three 2.04x, Healthy_sliced three_merged 2.69x, Severe_lobe_c3 three 2.34x, MCI_lobe_c3 three_merged 2.44x | sensitive:  | sensitive: Healthy_sliced_new three_merged 2.53x, Severe_lobe three 2.04x, Healthy_sliced three_merged 2.69x, Severe_lobe_c3 three 2.34x, MCI_lobe_c3 three_merged 2.44x |
| label Healthy_sliced_new binary (Normal) | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| label Healthy_sliced_new three (Normal) | not determined (< 2x) | robust (>= 3x) | not determined (< 2x) |
| label Healthy_sliced_new three_merged (Normal) | sensitive (2-3x) | robust (>= 3x) | sensitive (2-3x) |
| label Mild_lobe binary (AD) | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| label Mild_lobe three (UNCERTAIN) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Mild_lobe three_merged (Mild+Moderate) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Moderate_lobe binary (AD) | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| label Moderate_lobe three (Mild) | not determined (< 2x) | robust (>= 3x) | not determined (< 2x) |
| label Moderate_lobe three_merged (Mild+Moderate) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Severe_lobe binary (AD) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Severe_lobe three (Severe) | sensitive (2-3x) | robust (>= 3x) | sensitive (2-3x) |
| label Severe_lobe three_merged (Severe) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Healthy_sliced binary (Normal) | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| label Healthy_sliced three (Normal) | not determined (< 2x) | robust (>= 3x) | not determined (< 2x) |
| label Healthy_sliced three_merged (Normal) | sensitive (2-3x) | robust (>= 3x) | sensitive (2-3x) |
| label Mild_lobe_new binary (AD) | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| label Mild_lobe_new three (Mild) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Mild_lobe_new three_merged (Mild+Moderate) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Moderate_lobe_c3 binary (AD) | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| label Moderate_lobe_c3 three (Mild) | not determined (< 2x) | robust (>= 3x) | not determined (< 2x) |
| label Moderate_lobe_c3 three_merged (Mild+Moderate) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Severe_lobe_c3 binary (AD) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Severe_lobe_c3 three (Severe) | sensitive (2-3x) | robust (>= 3x) | sensitive (2-3x) |
| label Severe_lobe_c3 three_merged (Severe) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label LeftOnly_test_c3 binary (AD) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label LeftOnly_test_c3 three (Normal) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label LeftOnly_test_c3 three_merged (Normal) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label MCI_lobe_c3 binary (Normal) | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| label MCI_lobe_c3 three (Normal) | not determined (< 2x) | robust (>= 3x) | not determined (< 2x) |
| label MCI_lobe_c3 three_merged (Normal) | sensitive (2-3x) | robust (>= 3x) | sensitive (2-3x) |
| label RightOnly_test binary (AD) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label RightOnly_test three (Normal) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label RightOnly_test three_merged (Mild+Moderate) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Test_B binary (AD) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Test_B three (Normal) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| label Test_B three_merged (Normal) | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 6: mask shift 0.319 dB / R31 yardstick | not determined (< 2x) | not determined (< 2x) | sensitive (2-3x) |
| claim 10: smallest lobe R21 stage gap / (2 x R21 yardstick) | does not separate | separates | does not separate |
| claim 32: R21 rise of LeftOnly / R21 yardstick | not determined (< 2x) | sensitive (2-3x) | not determined (< 2x) |
| claim 32: R21 rise of Test_B / R21 yardstick | not determined (< 2x) | sensitive (2-3x) | not determined (< 2x) |
| claim 32: R21 rise of RightOnly / R21 yardstick | not determined (< 2x) | sensitive (2-3x) | not determined (< 2x) |
| claim 29: R21 mirror-twin difference 0.133 dB / R21 yardstick | within | within | within |
| claim 15 imaging LR LeftOnly_test_c3 [Tikhonov dS (primary), Healthy_sliced] | not determined (< 2x) | not determined (< 2x) | robust (>= 3x) |
| claim 15 imaging LR RightOnly_test [Tikhonov dS (primary), Healthy_sliced] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR Test_B [Tikhonov dS (primary), Healthy_sliced] | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 15 imaging LR LeftOnly_test_c3 [Tikhonov dS (primary), Healthy_sliced_new] | not determined (< 2x) | not determined (< 2x) | robust (>= 3x) |
| claim 15 imaging LR RightOnly_test [Tikhonov dS (primary), Healthy_sliced_new] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR Test_B [Tikhonov dS (primary), Healthy_sliced_new] | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 15 imaging LR LeftOnly_test_c3 [Tikhonov log (gain-inv.), Healthy_sliced] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR RightOnly_test [Tikhonov log (gain-inv.), Healthy_sliced] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR Test_B [Tikhonov log (gain-inv.), Healthy_sliced] | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 15 imaging LR LeftOnly_test_c3 [Tikhonov log (gain-inv.), Healthy_sliced_new] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR RightOnly_test [Tikhonov log (gain-inv.), Healthy_sliced_new] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR Test_B [Tikhonov log (gain-inv.), Healthy_sliced_new] | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 15 imaging LR LeftOnly_test_c3 [whitened log (post-hoc), Healthy_sliced] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR RightOnly_test [whitened log (post-hoc), Healthy_sliced] | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 15 imaging LR Test_B [whitened log (post-hoc), Healthy_sliced] | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 15 imaging LR LeftOnly_test_c3 [whitened log (post-hoc), Healthy_sliced_new] | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 15 imaging LR RightOnly_test [whitened log (post-hoc), Healthy_sliced_new] | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 15 imaging LR Test_B [whitened log (post-hoc), Healthy_sliced_new] | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| claim 16 LeftOnly phase cross-ratios >= 3x [band mean 3.2-4.2] | 2 | 2 | 16 |
| C6 P2 RightOnly phase cross-ratios >= 3x [band mean 3.2-4.2] | 2 | 2 | 11 |
| Test_B phase cross-ratios >= 3x [band mean 3.2-4.2] | 0 | 0 | 0 |
| claim 16 LeftOnly phase cross-ratios >= 3x [3.30-3.65 GHz] | 2 | 2 | 6 |
| C6 P2 RightOnly phase cross-ratios >= 3x [3.30-3.65 GHz] | 4 | 4 | 7 |
| Test_B phase cross-ratios >= 3x [3.30-3.65 GHz] | 2 | 2 | 5 |
| claim 17: LeftOnly LR resonance shift vs null max (MHz) | +1.91 vs 2.86: not beyond | +1.91 vs 2.86: not beyond | +1.91 vs 0.80: beyond |
| claim 18/33 T2 refl. vs T6 refl. LeftOnly_test_c3 | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 18/33 T2 refl. vs T6 refl. RightOnly_test | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 18/33 T2 refl. vs T6 refl. Test_B | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 18/33 T3 refl. vs T5 refl. LeftOnly_test_c3 | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 18/33 T3 refl. vs T5 refl. RightOnly_test | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 18/33 T3 refl. vs T5 refl. Test_B | robust (>= 3x) | robust (>= 3x) | robust (>= 3x) |
| claim 33: Test_B per-pair reading S2 left and S5 right, both >= 3x | holds | holds | holds |
| claim 19 LeftOnly phase pair T2-T3 vs T5-T6 (3.30-3.65) / null max | sensitive (2-3x) | sensitive (2-3x) | robust (>= 3x) |
| claim 19 LeftOnly phase pair T3-T4 vs T4-T5 (3.30-3.65) / null max | sensitive (2-3x) | sensitive (2-3x) | sensitive (2-3x) |
| claim 19 LeftOnly phase pair T1-T2 vs T1-T6 (3.30-3.65) / null max | not determined (< 2x) | not determined (< 2x) | robust (>= 3x) |
| claim 28 / C6 P1 within tolerance (post hoc only) | 21/26 | 21/26 | 12/26 |
| C6 P4 within yardstick (post hoc only) | R31 True, R21 True, R32 True | R31 True, R21 True, R32 True | R31 True, R21 True, R32 True |
| claim 35: mirror rulers raised above the 9-null rulers, by family | {'phase cross-ratio': 24, 'power LR index': 2, 'power pair': 2, 'power cross-ratio': 14, 'phase pair': 1} | {'phase cross-ratio': 24, 'power LR index': 2, 'power pair': 1, 'power cross-ratio': 3, 'phase pair': 1} | {'phase cross-ratio': 14, 'power pair': 2, 'power cross-ratio': 14, 'phase pair': 1} |
| Test_B front-back, all paths | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| Test_B front-back, neighbour paths | not determined (< 2x) | not determined (< 2x) | not determined (< 2x) |
| Test_B mirror side (protocol rule) | mixed (3 left, 1 right) | mixed (3 left, 1 right) | mixed (3 left, 1 right) |
| claim 34: Test_B pattern fit (contrast / call) | rejected; call 123456 (diffuse); sectors S1 a3.5, S2 a3.5, S3 a3.5, S4 a3.5, S5 a3.5, S6 a3.5 | rejected; call 123456 (diffuse); sectors S1 a3.5, S2 a3.5, S3 a3.5, S4 a3.5, S5 a3.5, S6 a3.5 | accepted; call 25; sectors S1 u1.2, S2 u1.5, S3 u0.8, S4 u1.4, S5 u0.9, S6 u1.3 |
| claim 34: Null_rot07 as target (leave-one-out rulers) must give 'none' | none (contrast 0.97x) | none (contrast 0.97x) | none (contrast 1.54x) |
| claim 34: Null_rot19 as target (leave-one-out rulers) must give 'none' | none (contrast 0.63x) | none (contrast 0.63x) | n/a |
| claim 34: Null_rot31 as target (leave-one-out rulers) must give 'none' | none (contrast 0.98x) | none (contrast 0.98x) | none (contrast 1.55x) |
| claim 34: Null_rot43 as target (leave-one-out rulers) must give 'none' | none (contrast 1.02x) | none (contrast 1.02x) | none (contrast 1.58x) |
