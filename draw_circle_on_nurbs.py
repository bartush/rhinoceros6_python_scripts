# -*- coding: utf-8 -*-

import Rhino
import Rhino.Geometry as rg
import System.Drawing.Color as syscolor
from scriptcontext import doc, sticky
from math import sin, cos, pi

# global constants
TOLERANCE = 0.01
RESOLUTION = 100
DIAMETER_INCREMENT = 0.1

def CircleOnNurbsSurface(center_point, nurbs_surf, diameter, resolution):
    [ _, center_point_u, center_point_v ] = nurbs_surf.ClosestPoint(center_point)
    surf_normal = nurbs_surf.NormalAt(center_point_u, center_point_v)
    alpha = 0
    points = []
    uv_radius = 0.01
    for _ in range(resolution+1):
        alpha += (2*pi)/resolution
        point_u = center_point_u + uv_radius * cos(alpha)
        point_v = center_point_v + uv_radius * sin(alpha)
        point = nurbs_surf.PointAt(point_u, point_v)
        radius_line = rg.LineCurve(center_point, point).ToNurbsCurve()
        uv_radius_line = nurbs_surf.InterpolatedCurveOnSurface([center_point, point], TOLERANCE)
        length = radius_line.GetLength()
        #length = radius_line.GetLength()
        if length < diameter/2:
            factor = 0.8*diameter/length
            point_u = center_point_u + uv_radius * factor * cos(alpha)
            point_v = center_point_v + uv_radius * factor * sin(alpha)
            #if nurbs_surf.Domain(0).IncludesParameter(point_u) and nurbs_surf.Domain(1).IncludesParameter(point_v):
            point = nurbs_surf.PointAt(point_u, point_v)
            #radius_line = rg.LineCurve(center_point, point).ToNurbsCurve()
            #uv_radius_line = radius_line.PullToBrepFace(nurbs_surf.ToBrep().Faces[0], TOLERANCE)[0]
            uv_radius_line = nurbs_surf.InterpolatedCurveOnSurface([center_point, point], TOLERANCE)
            #else: point = None
        #[_ , t ] = uv_radius_line.LengthParameter(diameter/2)
        point = uv_radius_line.PointAtLength(diameter/2)
        #point = radius_line.PointAtLength(diameter/2)
        if point: points.append(point)
    #print len(points)
    #nurbs_curve = nurbs_surf.InterpolatedCurveOnSurface(points, TOLERANCE)
    #nurbs_curve.MakeClosed(0)
    curve = rg.Curve.CreateInterpolatedCurve(points, 3, rg.CurveKnotStyle.ChordPeriodic)
    curve.MakeClosed(TOLERANCE)
    
    return curve

def SelectNurbsSurface():
    filter = Rhino.DocObjects.ObjectType.Surface
    rc, objref = Rhino.Input.RhinoGet.GetOneObject("Selet surface", False, filter)
    if not objref or rc != Rhino.Commands.Result.Success: 
        print "Surface is not selected!"
        return None
    else:
        #print objref.Face()
        return objref.Face()

def SetCircle(brep_face):
    def CustomMouseMove(sender, args):
        if args.Source.Tag.has_key("old_point"):
            old_point = args.Source.Tag["old_point"]
        else:
            old_point = args.WindowPoint
        if args.ControlKeyDown:
            if args.WindowPoint.Y > old_point.Y: 
                args.Source.Tag["activeDiameter"] -= DIAMETER_INCREMENT
            else: 
                args.Source.Tag["activeDiameter"] += DIAMETER_INCREMENT
        args.Source.Tag["old_point"] = args.WindowPoint
    def dynamic_draw_curve(sender, args):
        try:
            curve = CircleOnNurbsSurface(args.CurrentPoint, brep_face, args.Source.Tag["activeDiameter"], int(RESOLUTION/2))
            args.Display.DrawCurve(curve, syscolor.HotPink, 3)
        except Exception as e: print e
    if sticky.has_key("activeDiameter"):
        activeDiameter = sticky["activeDiameter"]
    else:
        activeDiameter = 1
        sticky["activeDiameter"] = activeDiameter
    gp = Rhino.Input.Custom.GetPoint()
    dblOption_activeDiameter = Rhino.Input.Custom.OptionDouble(activeDiameter)
    gp.Tag = {"activeDiameter" : activeDiameter}
    gp.AddOptionDouble("Diameter", dblOption_activeDiameter)
    gp.AcceptUndo(False)
    gp.EnableTransparentCommands(True)
    gp.Constrain( brep_face, True)
    gp.SetCommandPrompt("Set circle position")
    gp.MouseMove   += CustomMouseMove
    gp.DynamicDraw += dynamic_draw_curve
    while gp.Get()!= Rhino.Input.GetResult.Cancel:
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return None
        if gp.Result() != Rhino.Input.GetResult.Option:
            
            gp.Tag["point"] = gp.Point()
            curve = CircleOnNurbsSurface(gp.Tag["point"], brep_face, gp.Tag["activeDiameter"], RESOLUTION)
            doc.Objects.AddPoint(gp.Tag["point"])
            doc.Objects.AddCurve(curve.PullToBrepFace(brep_face, TOLERANCE)[0])
        if gp.Result() == Rhino.Input.GetResult.Option:
            gp.Tag["activeDiameter"] = dblOption_activeDiameter.CurrentValue
            sticky["activeDiameter"] = gp.Tag["activeDiameter"]

if __name__ == "__main__":
    try:
        brep_face =  SelectNurbsSurface()
        SetCircle(brep_face)
    except Exception as e:
        print e