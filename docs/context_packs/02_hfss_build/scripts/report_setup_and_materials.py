# ----------------------------------------------------------------------------
# READ-ONLY report for project new_with_slices (changes nothing in the model).
# For every design: prints all Setup1 properties, the material of every brain object,
# and exports the convergence table to D:/Jatin/conv/<design>_Setup1.conv
# Ansys Electronics Desktop 2024.2.   Tools > Run Script...   (any design active)
# Then copy the Message Manager text + the .conv files to Claude / the analysis session.
# ----------------------------------------------------------------------------
import ScriptEnv, os
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()
OUT = "D:/Jatin/conv"
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def msg(t):
    oDesktop.AddMessage("", "", 0, "[report] " + t)


BRAIN = ("CSF_outer", "HippocampusAD", "Ventricle_CSF")
for name in oProject.GetTopDesignList():
    d = name.split(";")[-1]
    oProject.SetActiveDesign(d)
    oDesign = oProject.GetActiveDesign()
    msg("================ %s ================" % d)

    # --- Setup1: every property HFSS exposes (Max Delta S, passes, freq, ...) ---
    try:
        for p in oDesign.GetProperties("HfssTab", "AnalysisSetup:Setup1"):
            try:
                msg("Setup1  %-36s = %s" % (p, oDesign.GetPropertyValue("HfssTab", "AnalysisSetup:Setup1", p)))
            except Exception:
                pass
    except Exception as e:
        msg("Setup1 properties not readable: %s" % e)

    # --- materials of brain objects ---
    oEditor = oDesign.SetActiveEditor("3D Modeler")
    for o in oEditor.GetObjectsInGroup("Solids"):
        if o in BRAIN or o.startswith("GM_") or o.startswith("WM_"):
            m = oEditor.GetPropertyValue("Geometry3DAttributeTab", o, "Material")
            msg("object  %-22s material %s" % (o, m))

    # --- convergence table (passes, Max Mag Delta S, CONVERGED or not) ---
    try:
        f = "%s/%s_Setup1.conv" % (OUT, d)
        oDesign.GetModule("Solutions").ExportConvergence("Setup1", "", f, True)
        msg("convergence exported -> %s" % f)
    except Exception as e:
        msg("no convergence data for %s (%s)" % (d, e))
msg("done")
