# ----------------------------------------------------------------------------
# Localisation test design: LeftOnly_test = Mild_lobe with the RIGHT side healthy.
#   Diseased : S2 TemporalL (CSF +7.5 mm), S3 ParietalL (CSF +11.5 mm), Mild materials
#   Healthy  : S1 Frontal, S4 Occipital, S5 ParietalR, S6 TemporalR
#   Unchanged from Mild_lobe: hippocampus (17.5 mm, Mild) and CSF material (Mild),
#   both central/global, so they cannot create a left-right difference.
# Run after make_stage_designs.py.  Tools > Run Script...
# ----------------------------------------------------------------------------
import time
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()

SRC, TARGET = "Mild_lobe", "LeftOnly_test"
GM_H, WM_H = "Gray_Matter_healthy", "WhiteMatterHealthy"
RIGHT = ["S5_ParietalR", "S6_TemporalR"]


def msg(t):
    oDesktop.AddMessage("", "", 0, "[left-only] " + t)


def set_var(design, name, value):
    design.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
        ["NAME:PropServers", "LocalVariables"],
        ["NAME:ChangedProps", ["NAME:" + name, "Value:=", value]]]])


def assign(editor, objs, material):
    editor.AssignMaterial(["NAME:Selections", "Selections:=", ",".join(objs)],
                          ["NAME:Attributes", "MaterialValue:=", '"%s"' % material,
                           "SolveInside:=", True, "ShellElement:=", False,
                           "ShellElementThickness:=", "nan ", "IsMaterialEditable:=", True,
                           "UseMaterialAppearance:=", False, "IsLightweight:=", False])


if TARGET not in oProject.GetTopDesignList():
    new = None
    for attempt in range(3):
        oProject.SetActiveDesign(SRC)
        before = set(oProject.GetTopDesignList())
        try:
            oProject.CopyDesign(SRC)
            oProject.Paste()
        except Exception:
            time.sleep(3)
            continue
        added = [x for x in oProject.GetTopDesignList() if x not in before]
        if added:
            new = added[0]
            break
        time.sleep(3)
    if new is None:
        raise Exception("copy of %s failed - copy/paste it by hand, rename it %s, rerun" % (SRC, TARGET))
    d = oProject.SetActiveDesign(new)
    d.RenameDesignInstance(new, TARGET)
    oProject.Save()

d = oProject.SetActiveDesign(TARGET)
ed = d.SetActiveEditor("3D Modeler")
set_var(d, "e_S5", "0mm")
set_var(d, "e_S6", "0mm")
assign(ed, ["GM_" + t for t in RIGHT], GM_H)
assign(ed, ["WM_" + t for t in RIGHT], WM_H)
oProject.Save()
msg("%s: left temporal + left parietal diseased, right side healthy; validation %s"
    % (TARGET, d.ValidateDesign()))
