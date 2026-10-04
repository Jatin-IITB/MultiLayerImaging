# ----------------------------------------------------------------------------
# READ-ONLY geometry audit for the ACTIVE design (run it on Healthy_sliced).
# Changes nothing. Tools > Run Script...  Copy the whole Message Manager output to Claude.
#
# Prints:
#  1. every solid: material, vertex-centroid (x,y,z) mm, azimuth deg, polar deg, distance from origin,
#     and the radius expression if it is a sphere  -> shows where each antenna part really sits
#  2. every excitation/terminal name                 -> ties Port k / T-label to a physical object
#  3. every design variable and its evaluated value  -> flags leftovers such as r_csf = 95.5 mm
# ----------------------------------------------------------------------------
import ScriptEnv, math
ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oProject = oDesktop.GetActiveProject()
oDesign = oProject.GetActiveDesign()
oEditor = oDesign.SetActiveEditor("3D Modeler")


def msg(t):
    oDesktop.AddMessage("", "", 0, "[geom] " + t)


def centroid(obj):
    try:
        ids = oEditor.GetVertexIDsFromObject(obj)
        if not ids:
            return None
        pts = [[float(v) for v in oEditor.GetVertexPosition(i)] for i in ids]
        n = float(len(pts))
        return [sum(p[k] for p in pts) / n for k in range(3)], len(pts)
    except Exception:
        return None


msg("design: " + oDesign.GetName())
# units of the modeler (vertex positions are returned in model units)
try:
    msg("model units: " + oEditor.GetModelUnits())
except Exception:
    pass

for o in oEditor.GetObjectsInGroup("Solids"):
    try:
        mat = oEditor.GetPropertyValue("Geometry3DAttributeTab", o, "Material")
    except Exception:
        mat = "?"
    rad = ""
    try:
        rad = oEditor.GetPropertyValue("Geometry3DCmdTab", o + ":CreateSphere:1", "Radius")
    except Exception:
        pass
    c = centroid(o)
    if c is None:
        msg("%-26s %-22s (no vertices: sphere/curved)  radius=%s" % (o, mat, rad))
        continue
    (x, y, z), nv = c
    r = math.sqrt(x * x + y * y + z * z)
    az = math.degrees(math.atan2(y, x))
    pol = math.degrees(math.acos(z / r)) if r > 0 else 0.0
    msg("%-26s %-22s c=(%8.2f,%8.2f,%8.2f) az=%7.1f pol=%6.1f d=%7.2f nv=%d %s"
        % (o, mat, x, y, z, az, pol, r, nv, ("radius=" + rad) if rad else ""))

for o in oEditor.GetObjectsInGroup("Sheets"):
    c = centroid(o)
    if c:
        (x, y, z), nv = c
        r = math.sqrt(x * x + y * y + z * z)
        msg("SHEET %-20s c=(%8.2f,%8.2f,%8.2f) az=%7.1f d=%7.2f"
            % (o, x, y, z, math.degrees(math.atan2(y, x)), r))

try:
    oB = oDesign.GetModule("BoundarySetup")
    msg("excitations: " + ", ".join(oB.GetExcitations()))
except Exception as e:
    msg("excitations not readable: %s" % e)

for v in oDesign.GetVariables():
    try:
        msg("var %-20s = %-14s -> %s" % (v, oDesign.GetVariableValue(v), oDesign.GetVariableValue(v)))
    except Exception:
        pass
msg("done")
