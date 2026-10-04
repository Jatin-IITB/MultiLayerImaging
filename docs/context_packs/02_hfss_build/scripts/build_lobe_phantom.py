# ----------------------------------------------------------------------------
# Lobe-sector phantom, SCRIPT 1: rebuild gray + white matter as 6 lobe sectors
# in the ACTIVE design (your Healthy copy in project new_with_slices).
# Ansys Electronics Desktop 2024.2.   Run: Tools > Run Script...
#
# BEFORE running: in the history tree expand CSF_outer, right-click its
# "Subtract" and Delete it (CSF_outer must be a plain solid sphere, r = 83.5 mm).
#
# Your objects (from the tree): CSF_outer, Gray_Matter, White_MatterAD, HippocampusAD
#
# Result (Healthy, all e = 0 mm):
#   GM_S1_Frontal .. GM_S6_TemporalR : sphere(83 - e_Sk) in wedge k, minus white
#   WM_S1_Frontal .. WM_S6_TemporalR : sphere(76 - e_Sk) in wedge k, minus a 25 mm hole
#   HippocampusAD                    : radius r_hip (25 mm healthy)
#   CSF_outer                        : sphere(83.5) minus all of the above
#                                      -> fills the 0.5 mm layer, any lobe where the
#                                         cortex moved in, and the ventricle gap
#                                         around a shrunken hippocampus
# Sector k is centred on antenna Tk: S1 at -90 deg (-Y, T1 = nose), +60 deg each.
# ----------------------------------------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
oEditor = oDesign.SetActiveEditor("3D Modeler")

CSF, GM_OLD, WM_OLD, HIP = "CSF_outer", "Gray_Matter", "White_MatterAD", "HippocampusAD"
SECTORS = [("S1", "Frontal",   (240, 190, 40)),
           ("S2", "TemporalL", (200, 60, 50)),
           ("S3", "ParietalL", (140, 90, 190)),
           ("S4", "Occipital", (60, 140, 220)),
           ("S5", "ParietalR", (140, 90, 190)),
           ("S6", "TemporalR", (200, 60, 50))]


def msg(t, level=0):
    oDesktop.AddMessage("", "", level, "[lobe phantom] " + t)


def solids():
    return list(oEditor.GetObjectsInGroup("Solids"))


def history(obj):
    try:
        return list(oEditor.GetChildObject(obj).GetChildNames())
    except Exception:
        return []


def radius(obj):
    try:
        return oEditor.GetPropertyValue("Geometry3DCmdTab", obj + ":CreateSphere:1", "Radius")
    except Exception:
        return "?"


def material_of(obj):
    return oEditor.GetPropertyValue("Geometry3DAttributeTab", obj, "Material").strip('"')


def add_var(name, value):
    try:
        oDesign.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
            ["NAME:PropServers", "LocalVariables"],
            ["NAME:NewProps", ["NAME:" + name, "PropType:=", "VariableProp",
                               "UserDef:=", True, "Value:=", value]]]])
    except Exception:
        oDesign.ChangeProperty(["NAME:AllTabs", ["NAME:LocalVariableTab",
            ["NAME:PropServers", "LocalVariables"],
            ["NAME:ChangedProps", ["NAME:" + name, "Value:=", value]]]])


def attrs(name, color, transp=0.3):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "",
            "Color:=", "(%d %d %d)" % color, "Transparency:=", transp,
            "PartCoordinateSystem:=", "Global", "UDMId:=", "",
            "MaterialValue:=", '"vacuum"', "SurfaceMaterialValue:=", '""',
            "SolveInside:=", True, "ShellElement:=", False,
            "ShellElementThickness:=", "0mm", "IsMaterialEditable:=", True,
            "UseMaterialAppearance:=", False, "IsLightweight:=", False]


def sphere(name, r, color):
    oEditor.CreateSphere(["NAME:SphereParameters", "XCenter:=", "0mm", "YCenter:=", "0mm",
                          "ZCenter:=", "0mm", "Radius:=", r], attrs(name, color))


def wedge(name, start_deg):
    """60 deg wedge about +Z covering azimuth start..start+60 (|z|, rho <= 240 mm)."""
    oEditor.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
                             "XStart:=", "0mm", "YStart:=", "0mm", "ZStart:=", "-120mm",
                             "Width:=", "240mm", "Height:=", "240mm", "WhichAxis:=", "Y"],
                            attrs(name, (200, 200, 200)))
    oEditor.SweepAroundAxis(["NAME:Selections", "Selections:=", name, "NewPartsModelFlag:=", "Model"],
                            ["NAME:AxisSweepParameters", "DraftAngle:=", "0deg", "DraftType:=", "Round",
                             "CheckFaceFaceIntersection:=", False, "ClearAllIDs:=", False,
                             "SweepAxis:=", "Z", "SweepAngle:=", "60deg", "NumOfSegments:=", "0"])
    oEditor.Rotate(["NAME:Selections", "Selections:=", name, "NewPartsModelFlag:=", "Model"],
                   ["NAME:RotateParameters", "RotateAxis:=", "Z", "RotateAngle:=", "%gdeg" % start_deg])


def intersect(keep, tool):
    oEditor.Intersect(["NAME:Selections", "Selections:=", keep + "," + tool],
                      ["NAME:IntersectParameters", "KeepOriginals:=", False])
    if keep not in solids():
        raise Exception("Intersect renamed %s - send this message to Claude" % keep)


def subtract(blank, tools):
    oEditor.Subtract(["NAME:Selections", "Blank Parts:=", blank, "Tool Parts:=", ",".join(tools)],
                     ["NAME:SubtractParameters", "KeepOriginals:=", True])


def assign(objs, material):
    oEditor.AssignMaterial(["NAME:Selections", "Selections:=", ",".join(objs)],
                           ["NAME:Attributes", "MaterialValue:=", '"%s"' % material,
                            "SolveInside:=", True, "ShellElement:=", False,
                            "ShellElementThickness:=", "nan ", "IsMaterialEditable:=", True,
                            "UseMaterialAppearance:=", False, "IsLightweight:=", False])


# ---- 0. pre-flight: report and stop if CSF_outer is still a shell ------------------
names = solids()
for o in names:
    if o in (CSF, GM_OLD, WM_OLD, HIP) or "sphere" in o.lower() or o in ("Skull", "Fat", "Skin"):
        msg("%-22s radius %-22s material %-22s history %s" % (o, radius(o), material_of(o), history(o)))
for need in (CSF, GM_OLD, WM_OLD, HIP):
    if need not in names:
        raise Exception("object %s not found - stop" % need)
if any("Subtract" in h for h in history(CSF)):
    raise Exception("CSF_outer still has a Subtract. Delete it in the history tree, then rerun.")

mat_gm, mat_wm = material_of(GM_OLD), material_of(WM_OLD)
msg("healthy gray material = %s, white material = %s" % (mat_gm, mat_wm))

# ---- 1. variables ----------------------------------------------------------------
for tag, _, _ in SECTORS:
    add_var("e_" + tag, "0mm")
add_var("r_hip", "25mm")

# ---- 2. remove old gray/white (and the clone that came back from the CSF Subtract) --
old = [GM_OLD, WM_OLD] + [o for o in solids() if o.startswith(GM_OLD + "_")]
oEditor.Delete(["NAME:Selections", "Selections:=", ",".join(old)])
msg("deleted %s" % old)

# hippocampus radius -> r_hip
oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DCmdTab",
    ["NAME:PropServers", HIP + ":CreateSphere:1"],
    ["NAME:ChangedProps", ["NAME:Radius", "Value:=", "r_hip"]]]])

# ---- 3. build the 12 sector pieces --------------------------------------------------
sphere("VentHole", "25mm", (255, 255, 255))           # fixed 25 mm hole in white matter
pieces = []
for k, (tag, lobe, col) in enumerate(SECTORS):
    start = -120 + 60 * k
    wm, gm = "WM_%s_%s" % (tag, lobe), "GM_%s_%s" % (tag, lobe)
    sphere(wm, "76mm - e_" + tag, tuple(min(255, c + 70) for c in col))
    wedge("Wt_" + wm, start)
    intersect(wm, "Wt_" + wm)
    subtract(wm, ["VentHole"])
    sphere(gm, "83mm - e_" + tag, col)
    wedge("Wt_" + gm, start)
    intersect(gm, "Wt_" + gm)
    subtract(gm, [wm])
    pieces += [gm, wm]
    msg("built %s, %s  (azimuth %d..%d deg)" % (gm, wm, start, start + 60))
oEditor.Delete(["NAME:Selections", "Selections:=", "VentHole"])

# ---- 4. CSF = sphere(83.5) minus everything inside --------------------------------
subtract(CSF, pieces + [HIP])

# ---- 5. healthy materials, save, validate -------------------------------------------
assign([p for p in pieces if p.startswith("GM_")], mat_gm)
assign([p for p in pieces if p.startswith("WM_")], mat_wm)
oProject.Save()
msg("validation: %s" % oDesign.ValidateDesign())
msg("done - 12 sector objects built. Take a top-view screenshot for checking.")
