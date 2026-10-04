# Blind score: Test_B — PRIMARY verdict **PASS**

Truth (supplied after the reconstruction): `{"e": [0, 11.5, 0, 0, 7.5, 0], "tissue_stage": "Mild", "csf_stage": "Mild", "hip_stage": "Mild", "r_hip": 17.5, "source": "user message after all three sessions committed estimates: e_S1..e_S6 = 0/11.5/0/0/7.5/0 mm, r_hip 17.5, GM/WM_Mild in S2 and S5 only, HIP_Mild, CSF_Mild"}`

| variant | role | stage est / true | lobe calls /6 (C1) | stage (C2) | truth in 90% /6 (C3) | fit | overall |
|---|---|---|---|---|---|---|---|
| standard_H6 | PRIMARY | Mild / Mild | 6 (PASS) | True | 6 (met) | 0.46 OK | **PASS** |
| gainfree_H6 | secondary | Mild / Mild | 6 (PASS) | True | 5 (met) | 0.77 OK | **PASS** |
| standard_H7 | secondary | Mild / Mild | 6 (PASS) | True | 5 (met) | 0.42 OK | **PASS** |
