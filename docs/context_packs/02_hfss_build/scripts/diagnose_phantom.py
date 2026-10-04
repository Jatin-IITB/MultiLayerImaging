# Read-only: prints every design variable and the radius of every sphere,
# including the hidden "tool" spheres used by the Subtract operations.
# Changes nothing.   Tools > Run Script...  with the Healthy design active.
import ScriptEnv
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
oEditor = oDesign.SetActiveEditor("3D Modeler")


def msg(t):
    oDesktop.AddMessage("", "", 0, "[diag] " + t)


for v in oDesign.GetVariables():
    msg("variable %-18s = %s" % (v, oDesign.GetVariableValue(v)))

objs = list(oEditor.GetObjectsInGroup("Solids"))
tools = ["Brain_sphere_1", "skull_sphere_1", "fat_sphere_1", "white_matter_mildAD_1",
         "Gray_Matter_1", "HippocampusAD_1"]
for o in objs + tools:
    try:
        r = oEditor.GetPropertyValue("Geometry3DCmdTab", o + ":CreateSphere:1", "Radius")
        msg("sphere %-22s radius = %s" % (o, r))
    except Exception:
        pass
for o in objs:
    try:
        h = list(oEditor.GetChildObject(o).GetChildNames())
        msg("history %-22s %s" % (o, h))
    except Exception:
        pass
