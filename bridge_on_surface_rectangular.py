# -*- coding: utf-8 -*-

import Rhino
import Rhino.Geometry as rg
import System.Drawing.Color as syscolor
import scriptcontext as sc
from scriptcontext import sticky
from math import sin, cos, pi
from System.Drawing.Color import FromArgb
from rhinoscriptsyntax import Redraw
from rhinoscriptsyntax import OffsetSurface, DeleteObject, FlipSurface


# global constants declaration

HEIGHT = 0.8
WIDTH = 0.5

def SelectNurbsSurface():
    filter = Rhino.DocObjects.ObjectType.Surface
    rc, objref = Rhino.Input.RhinoGet.GetOneObject("Selet surface", False, filter)
    if not objref or rc != Rhino.Commands.Result.Success: 
        print "Surface is not selected!"
        return None
    else:
        #print objref.Face()
        return objref.Face()

def BridgeContOnSurface( first_point, second_point, surface, l, w ):
    tmp_line = rg.LineCurve(first_point, second_point)
    mid_line = tmp_line.PullToBrepFace(surface, 0.1)[0]
    mid_line_length = mid_line.GetLength(mid_line.Domain)
    if mid_line_length <= l:
        end_point = second_point
    else:
        end_point = mid_line.PointAtLength(l)

    line = rg.LineCurve(first_point, end_point)
    mid_point = line.PointAt(line.Domain.Mid)
    (b, u ,v) = surface.ClosestPoint(mid_point)
    
    n = surface.NormalAt(u,v)
    plane = rg.Plane(mid_point, n)
    start_circle = rg.Circle(plane, first_point, w/2)
    end_circle =   rg.Circle(plane, end_point,   w/2)
    
    finish_point = rg.Point(  end_circle.ClosestPoint(first_point))
    start_point =  rg.Point(start_circle.ClosestPoint(end_point))
    start_point.Rotate ( pi/2, n, first_point)
    p0 = start_point.Location
    start_point.Rotate ( pi, n, first_point)
    p1 = start_point.Location
    finish_point.Rotate( pi/2, n, end_point)
    p2 = finish_point.Location
    finish_point.Rotate( pi, n, end_point)
    p3 = finish_point.Location
    geometry = []
    geometry.append(rg.LineCurve(p0, p3).ToNurbsCurve())
    geometry.append(rg.LineCurve(p0, p1).ToNurbsCurve())
    geometry.append(rg.LineCurve(p1, p2).ToNurbsCurve())
    geometry.append(rg.LineCurve(p2, p3).ToNurbsCurve())
    return geometry

def ShowBridge(obj, base_surf):
    base_color = FromArgb(0, 0,0, 0)
    cur = sc.doc.Layers.CurrentLayer
    layer_id = sc.doc.Layers.Find("Bridges", True)
    if not layer_id >= 0:
        layer_id = sc.doc.Layers.Add("Bridges", base_color)
    layer = Rhino.DocObjects.Layer()
    layer.Color = base_color
    sc.doc.Layers.Modify(layer, layer_id, True)
    sc.doc.Layers.SetCurrentLayerIndex(layer_id, True)
    #--- adding objecs
    if len(obj) > 0:
        crv_length_list = []
        for crv in obj:
            crv_length_list.append({'crv': crv, 'length' :crv.GetLength()})
        bridge_rails = sorted(crv_length_list, key = lambda x: x['length'], reverse = True)
        bridge_rails = bridge_rails[:2]
        bridge_rails[0] = bridge_rails[0]['crv']
        bridge_rails[1] = bridge_rails[1]['crv']
        normal_check_point = bridge_rails[0].PointAtStart
        bridge_surf = rg.NurbsSurface.CreateRuledSurface(bridge_rails[0],bridge_rails[1])
        
        (_, u1, v1) = bridge_surf.ClosestPoint(normal_check_point)
        (_, u2, v2) = base_surf.ClosestPoint(normal_check_point)
        bridge_surf_normal = bridge_surf.NormalAt(u1, v1)
        base_surf_normal   = base_surf.NormalAt(u2, v2)
        bridge_surf_id = sc.doc.Objects.AddSurface(bridge_surf)
        if not bridge_surf_normal.EpsilonEquals(base_surf_normal, 0.2):
            FlipSurface(bridge_surf_id, True)
        
        
        #bridge_cont.append(sc.doc.Objects.AddCurve(bridge_rails[1]['crv']))
        brep = OffsetSurface(bridge_surf_id, HEIGHT, 0.01, False, True)
        DeleteObject(bridge_surf_id)
        
    #------------
    sc.doc.Layers.SetCurrentLayerIndex(cur.SortIndex, True)
    Redraw()
    #group = sc.doc.Groups.Add(bridge_cont)
    return brep

def Set(surf):
    point_count = 0
    point1 = rg.Point3d(0,0,0)
    point2 = rg.Point3d(0,0,0)
    def CustomMouseMove(sender, args):
        if args.ShiftKeyDown:
            args.Source.Tag[0] = True
        else: args.Source.Tag[0] = False
    def dynamic_draw_curve(sender, args):
        UV_parallel_mode = args.Source.Tag[0]
        if UV_parallel_mode and point_count == 1: 
            (b1, U1, V1) = surf.ClosestPoint(point1)
            (b2, U2, V2) = surf.ClosestPoint(args.CurrentPoint)
            if b1 and b2:
                dU = abs(U1 - U2)
                dV = abs(V1 - V2)
                if dU >= dV: point = surf.PointAt(U2, V1)
                else:        point = surf.PointAt(U1, V2)
            else: point = args.CurrentPoint
            args.Source.Tag[1] = point
        else: point = args.CurrentPoint
        if point_count == 0:
            args.Display.DrawPoint (args.CurrentPoint, 0, 10, syscolor.HotPink)
            geometry = BridgeContOnSurface(point, point, surf, args.Source.Tag[2], args.Source.Tag[3])
            for obj in geometry:
                args.Display.DrawCurve (obj, syscolor.HotPink, 3)
        if point_count == 1:
            geometry = BridgeContOnSurface(point1, point, surf, args.Source.Tag[2], args.Source.Tag[3])
            for obj in geometry:
                args.Display.DrawCurve (obj, syscolor.HotPink, 3)
            args.Source.Tag[1] = point
    if sticky.has_key('Length') and sticky.has_key('Width'):
        Length = sticky['Length']
        Width = sticky['Width']
    else:
        Length = 50
        Width = WIDTH
        sticky['Length'] = Length
        sticky['Width'] = Width
    gp = Rhino.Input.Custom.GetPoint()
    dblOption_Length = Rhino.Input.Custom.OptionDouble(Length)
    dblOption_Width = Rhino.Input.Custom.OptionDouble(Width)
    gp.Tag = [False, point2, Length, Width]
    gp.AddOptionDouble("Length", dblOption_Length)
    gp.AddOptionDouble("Width", dblOption_Width)
    gp.AcceptUndo(False)
    gp.EnableTransparentCommands(True)
    gp.Constrain( surf, True)
    gp.SetCommandPrompt("Set first point")
    gp.MouseMove   += CustomMouseMove
    gp.DynamicDraw += dynamic_draw_curve
    while gp.Get()!= Rhino.Input.GetResult.Cancel:
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return None
        if gp.Result() != Rhino.Input.GetResult.Option:
            try:
                if point_count == 0: 
                    point1 = gp.Point()
                if point_count == 1: 
                    point2 = gp.Point() 
                    point2 = gp.Tag[1]
                    Length = gp.Tag[2]
                    Width  = gp.Tag[3]
                    geometry = BridgeContOnSurface(point1, point2,  surf, Length, Width)
                    pulled = []
                    for crv in geometry: 
                        p = crv.PullToBrepFace(surf, 0.1)
                        if len(p) > 0: pulled.append(p[0])
                    return ShowBridge(pulled, surf)
                point_count += 1
            except Exception as e: print e
        if gp.Result() == Rhino.Input.GetResult.Option:
            gp.Tag[2] = dblOption_Length.CurrentValue
            gp.Tag[3] = dblOption_Width.CurrentValue
            sticky['Length'] = gp.Tag[2]
            sticky['Width']  = gp.Tag[3]
        if  point_count == 1:
            gp.SetCommandPrompt("Set sdirection (press SHIFT to UV align)")


if __name__ == "__main__":
    try:
        surf =  SelectNurbsSurface()
        print surf
        while Set(surf):
            print 'New bridge is created!'
    except Exception as e:
        print  'main:', e 