# ----------------------------------------------------------------------------
# MCI_lobe mesh fix: make the thin CSF shell around the shrunken hippocampus an
# explicit object instead of "left-over" CSF.
#   Ventricle_CSF = sphere r = 25 mm (the hole in white matter), material CSF_Healthy
#   HippocampusAD (r_hip = 21.25 mm) sits inside it and keeps priority.
# Geometry and materials are unchanged; only how the region is described changes.
# Run with any design active.  Tools > Run Script...
# ----------------------------------------------------------------------------
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()
d = oProject.SetActiveDesign("MCI_lobe")
ed = d.SetActiveEditor("3D Modeler")

if "Ventricle_CSF" not in list(ed.GetObjectsInGroup("Solids")):
    ed.CreateSphere(["NAME:SphereParameters", "XCenter:=", "0mm", "YCenter:=", "0mm",
                     "ZCenter:=", "0mm", "Radius:=", "25mm"],
                    ["NAME:Attributes", "Name:=", "Ventricle_CSF", "Flags:=", "",
                     "Color:=", "(128 200 255)", "Transparency:=", 0.5,
                     "PartCoordinateSystem:=", "Global", "UDMId:=", "",
                     "MaterialValue:=", '"CSF_Healthy"', "SurfaceMaterialValue:=", '""',
                     "SolveInside:=", True, "ShellElement:=", False, "ShellElementThickness:=", "0mm",
                     "IsMaterialEditable:=", True, "UseMaterialAppearance:=", False,
                     "IsLightweight:=", False])
oProject.Save()
oDesktop.AddMessage("", "", 0, "[MCI fix] Ventricle_CSF added; validation %s" % d.ValidateDesign())
