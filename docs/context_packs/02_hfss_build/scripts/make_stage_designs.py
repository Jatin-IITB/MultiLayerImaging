# ----------------------------------------------------------------------------
# Lobe-sector phantom, step 2: create MCI_lobe, Mild_lobe, Moderate_lobe and
# Severe_lobe as copies of the sliced Healthy design, then set per-sector CSF
# expansion, hippocampus radius and materials.
#
# Run AFTER build_lobe_phantom.py, with the sliced Healthy design ACTIVE.
#
# Sources
#   Regions per stage and CSF expansion per lobe: Shehab et al., Results in
#   Engineering 27 (2025) 106350, Table 7 (same lobe order as Saied et al.,
#   IEEE JERM 2022, Table II).
#   Materials: Shehab Table 5 (3.241 GHz). Hippocampus radius: Shehab Table 6.
#   CSF is one connected fluid compartment: its material changes everywhere,
#   its thickness changes only in the affected lobes (gray/white pushed inward).
# ----------------------------------------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
BASE = oDesign.GetName()
oDefs = oProject.GetDefinitionManager()

CSF_OBJ = "CSF_Healthy"
HIPPO = "Hippocampus_healthy"
TAGS = ["S1_Frontal", "S2_TemporalL", "S3_ParietalL", "S4_Occipital", "S5_ParietalR", "S6_TemporalR"]

# material name: (eps_r, sigma S/m)  -- Shehab Table 5
MATS = {
    "GM_MCI": (47.7, 2.42),   "WM_MCI": (35.3, 1.65),   "HIP_MCI": (40.3, 5.203),   "CSF_MCI": (65.0, 4.27),
    "GM_Mild": (40.3, 5.203), "WM_Mild": (31.77, 2.39), "HIP_Mild": (39.11, 5.687), "CSF_Mild": (55.25, 4.91),
    "GM_Moderate": (39.11, 5.687), "WM_Moderate": (31.064, 2.722),
    "HIP_Moderate": (38.39, 5.92), "CSF_Moderate": (48.75, 5.337),
    "GM_Severe": (38.39, 5.92), "WM_Severe": (30.35, 2.88), "HIP_Severe": (37.2, 6.413), "CSF_Severe": (32.5, 6.405),
}

# CSF expansion per sector (mm), order S1..S6 = Frontal, TemporalL, ParietalL, Occipital, ParietalR, TemporalR
# 0 = sector unaffected (keeps healthy gray/white material). Shehab Table 7.
STAGES = {
    "MCI_lobe":      {"e": [0, 0, 0, 0, 0, 0],                   "r_hip": "21.25mm", "m": "MCI"},
    "Mild_lobe":     {"e": [0, 7.5, 11.5, 0, 11.5, 7.5],         "r_hip": "17.5mm",  "m": "Mild"},
    "Moderate_lobe": {"e": [11.5, 12.5, 15.5, 0, 15.5, 12.5],    "r_hip": "12.5mm",  "m": "Moderate"},
    "Severe_lobe":   {"e": [15.5, 17.5, 18, 11.5, 18, 17.5],     "r_hip": "7.5mm",   "m": "Severe"},
}


def msg(t):
    oDesktop.AddMessage("", "", 0, "[stages] " + t)


def ensure_material(name, eps, sig):
    if oDefs.DoesMaterialExist(name):
        return
    oDefs.AddMaterial(["NAME:" + name, "CoordinateSystemType:=", "Cartesian",
                       "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
                       "permittivity:=", str(eps), "conductivity:=", str(sig)])


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


for n, (e, s) in sorted(MATS.items()):
    ensure_material(n, e, s)
msg("materials ready")

for target, st in sorted(STAGES.items()):
    before = set(oProject.GetTopDesignList())
    oProject.CopyDesign(BASE)
    oProject.Paste()
    new = [d for d in oProject.GetTopDesignList() if d not in before][0]
    d = oProject.SetActiveDesign(new)
    d.RenameDesignInstance(new, target)
    d = oProject.SetActiveDesign(target)
    ed = d.SetActiveEditor("3D Modeler")
    m = st["m"]
    for tag, e in zip(TAGS, st["e"]):
        set_var(d, "e_" + tag.split("_")[0], "%gmm" % e)
        if e > 0:
            assign(ed, ["GM_" + tag], "GM_" + m)
            assign(ed, ["WM_" + tag], "WM_" + m)
    set_var(d, "r_hip", st["r_hip"])
    assign(ed, [HIPPO], "HIP_" + m)
    assign(ed, [CSF_OBJ], "CSF_" + m)
    msg("%s: e = %s mm, r_hip = %s, materials %s" % (target, st["e"], st["r_hip"], m))

oProject.Save()
msg("done: MCI_lobe, Mild_lobe, Moderate_lobe, Severe_lobe created. Validate each before solving.")
