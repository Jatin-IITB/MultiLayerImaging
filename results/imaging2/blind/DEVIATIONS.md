# Deviations from the blind protocol (BLIND_PROTOCOL.md, commit 595e9cb)

1. **Syntax error in the committed `imaging2/blind.py`, fixed before Test_B was loaded.**
   - **Cause:** after the in-sample dry run, a cosmetic edit wrapped the title of the blind overview figure. It wrote
     a literal line break inside an f-string. The module was committed without being re-run.
   - **Detection:** `python -m imaging2.blind run --file new_with_slices_Test_B.s6p --tag Test_B` failed with
     `SyntaxError` at compile time (blind.py line 159), before any code executed. Test_B was not read.
   - **Fix:** the line break becomes the `\n` escape in that title string. `git diff 595e9cb -- imaging2` shows this
     one line and nothing else.
   - **Check:** all modules compile. The in-sample dry run (LeftOnly, code test only) gives the same estimates as the
     pre-commit dry run: standard_H6 calls 0 1 1 0 0 0, ê 0/11.5/7.5/0/0/0 mm, χ²/dof 0.29; gainfree_H6 0.58;
     standard_H7 0.23.
   - **Effect on estimates, criteria or scoring:** none. The fix is committed before Test_B is loaded.
