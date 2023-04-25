import rhinoscriptsyntax as rs
import Rhino

def SelectCurves():
    curves = []
    gcurves = Rhino.Input.Custom.GetObject()
    gcurves.SetCommandPrompt("Select Curves to Offset")
    gcurves.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
    gcurves.SubObjectSelect = False
    gcurves.DeselectAllBeforePostSelect = False
    gcurves.OneByOnePostSelect = False
    gcurves.GetMultiple(1, 0)
    if gcurves.CommandResult()!=Rhino.Commands.Result.Success: 
        return gcurves.CommandResult()
    curveRefs = gcurves.Objects()
    for curveRef in curveRefs:
        curveobj = curveRef.Object()
        curve = curveRef.Curve()
        curves.append(curve)
        curveobj.Select(False)
    if not curveRefs: return Rhino.Commands.Result.Failure

    return curves

def OffsetSelectedCurvesInside(curve_list, dist):
    for curve in curve_list:
        centroid_point = rs.CurveAreaCentroid(curve)
        rs.OffsetCurve(curve, centroid_point[0], dist)

if __name__ == "__main__":
    curves = SelectCurves()
    #curves = rs.GetObjects()
    OffsetSelectedCurvesInside(curves, 0.15)