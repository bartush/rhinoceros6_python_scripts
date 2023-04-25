# -*- coding: utf-8 -*-

""" Script for creating leaves from polylines consisting of two curves. 
Resulting leaves are groups of surfaces wich have same degree as input curves
"""

import Rhino
from rhinoscriptsyntax import UnselectAllObjects, AddLoftSrf, OffsetSurface, DeleteObjects, ReverseCurve, ExplodeCurves, ExplodePolysurfaces, AddGroup, AddObjectsToGroup, GroupNames, SurfaceDegree, RebuildSurface, SurfacePointCount, EnableRedraw, DuplicateSurfaceBorder, FlipSurface
from scriptcontext import doc, sticky

def select_double_curve_polylines():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select two curve polylines")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
    go.SubObjectSelect = False
    go.GetMultiple(1,0) # minmum number = 1, maximum number = 0, 0 - means multiple
    result = go.CommandResult()
    UnselectAllObjects()
    if result == Rhino.Commands.Result.Success:
        curves = go.Objects()
        curves_count = len(curves)
        polycurve_ids = []
        for curve in curves:
            sub_object_curves = curve.Object().GetSubObjects()
            if sub_object_curves != None:
                sub_object_curves_count = len(sub_object_curves)
                if sub_object_curves_count == 2:
                    polycurve_ids.append(curve.ObjectId)
                    pass #breakpoint
                else:
                    print "One of selected polycurves has more than 2 curves!"
            else:
                print "One of selected polycurves is not PolyCurve!"
        return polycurve_ids
    elif result == Rhino.Commands.Result.Cancel:
        print "Selecting canceled!"
        return []
    else:
        print "Selecting Eroor!"
        return []

def set_thickness():
    if sticky.has_key("thickness"):
        thickness = sticky["thickness"]
    else:
        thickness = 1.1
        sticky["thickness"] = thickness
    result, new_thickness = Rhino.Input.RhinoGet.GetNumber("Set leaf thickness", acceptNothing = True, outputNumber = thickness)
    if result == Rhino.Commands.Result.Success:
        sticky["thickness"] = new_thickness
        return new_thickness
    else:
        return thickness

def new_group_name(name):
    count = 0
    existing_group_names = GroupNames()
    while True:
        new_group_name = name + str(count)
        if existing_group_names and new_group_name in existing_group_names:
            count += 1
        else:
            break
    return new_group_name

if __name__ == "__main__":
    polycurves = select_double_curve_polylines()
    if polycurves:
        thickness = set_thickness()
    for polycurve in polycurves:
        if polycurve:
            EnableRedraw(False)
            curve_ids = ExplodeCurves([polycurve], delete_input = True)
            ReverseCurve(curve_ids[0])
            top_srf   = AddLoftSrf(curve_ids, start = None, end = None, loft_type = 2, simplify_method = 0, value = 0, closed = False)
            bottom_srf = OffsetSurface(top_srf, -thickness, tolerance = None, both_sides = False, create_solid = False)
            RebuildSurface(bottom_srf, SurfaceDegree(top_srf, direction = 2), SurfacePointCount(top_srf))
            top_crv    = DuplicateSurfaceBorder(top_srf, type = 1)[0]
            bottom_crv = DuplicateSurfaceBorder(bottom_srf, type = 1)[0]
            FlipSurface(bottom_srf, flip = True)
            side_srf   = ExplodePolysurfaces(AddLoftSrf([top_crv, bottom_crv], start = None, end = None, loft_type = 2, simplify_method = 0, value = 0, closed = False), delete_input = True)
            DeleteObjects(curve_ids + [top_crv] + [bottom_crv])
            group_name = new_group_name("leaf")
            AddGroup(group_name)
            AddObjectsToGroup(top_srf, group_name)
            AddObjectsToGroup(bottom_srf, group_name)
            AddObjectsToGroup(side_srf, group_name)
            EnableRedraw(True)
            pass # breakepoint