import math
import Rhino
from rhinoscriptsyntax import ObjectColor
from scriptcontext import doc, sticky
import System.Drawing.Color as syscolor
from clr import Reference

def guid_object_type(id):
    return Rhino.DocObjects.ObjRef(id).Object().ObjectType

def select_surface():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select base surface to draw curve on")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface | Rhino.DocObjects.ObjectType.Mesh
    go.SubObjectSelect = True
    go.ChooseOneQuestion = True
    go.DisablePreSelect()
    go.DeselectAllBeforePostSelect = True
    go.OneByOnePostSelect = True
    go.GetMultiple(1,1) # minmum number = 1, maximum number = 1
    if go.CommandResult() != Rhino.Commands.Result.Success: 
        print("No surface is selected")
        return None
    type = go.Object(0).Object().ObjectType
    if type == Rhino.DocObjects.ObjectType.Surface or type == Rhino.DocObjects.ObjectType.Brep:
        surf_id= go.Object(0).ObjectId
        return type, surf_id
    elif type == Rhino.DocObjects.ObjectType.Mesh:
        mesh_id = go.Object(0).ObjectId
        return  type, mesh_id
    else: return None

def circle_on_surface(point, surface_id, diameter):
    type = guid_object_type(surface_id)
    if type == Rhino.DocObjects.ObjectType.Surface or type == Rhino.DocObjects.ObjectType.Brep:
        surf =  Rhino.DocObjects.ObjRef(surface_id).Surface()
        _, u, v = surf.ClosestPoint(point)
        normal = surf.NormalAt(u, v)
    elif type == Rhino.DocObjects.ObjectType.Mesh:
        mesh = Rhino.DocObjects.ObjRef(surface_id).Mesh()
        out_point = Reference[Rhino.Geometry.Point3d]()
        out_normal = Reference[Rhino.Geometry.Vector3d]()
        face_id = mesh.ClosestPoint(point, out_point, out_normal, 0.1)
        normal = out_normal.Value
    plane = Rhino.Geometry.Plane(point, normal)
    return Rhino.Geometry.Circle(plane, point, diameter/2)

def set_circle_on_surface(surface_id):
    def dynamic_draw_curve(sender, args):
        point = args.CurrentPoint
        diameter1 = args.Source.Tag["active_diameter"]
        diameter2 = args.Source.Tag["active_diameter"] + 2*args.Source.Tag["offset"]
        circle1 = circle_on_surface(point, surface_id, diameter1)
        args.Display.DrawCircle (circle1, syscolor.HotPink, 3)
        circle2 = circle_on_surface(point, surface_id, diameter2)
        args.Display.DrawCircle (circle2, syscolor.HotPink, 1)

    if sticky.has_key("cirle_on_surface_active_diameter") and sticky.has_key("cirle_on_surface_offset"):
        active_diameter = sticky["cirle_on_surface_active_diameter"]
        offset = sticky["cirle_on_surface_offset"]
    else:
        active_diameter = 1.0
        offset = 0.3
    gp = Rhino.Input.Custom.GetPoint()
    dbl_option_active_diameter = Rhino.Input.Custom.OptionDouble(active_diameter)
    dbl_option_offset = Rhino.Input.Custom.OptionDouble(offset)
    gp.Tag = {"active_diameter": active_diameter, "offset": offset}
    gp.AddOptionDouble("Diameter", dbl_option_active_diameter)
    gp.AddOptionDouble("Offset", dbl_option_offset)
    gp.AcceptUndo(False)
    gp.EnableTransparentCommands(True)
    gp.SetCommandPromptDefault("Diameter")
    type = Rhino.DocObjects.ObjRef(surface_id).Object().ObjectType
    if type == Rhino.DocObjects.ObjectType.Surface or type == Rhino.DocObjects.ObjectType.Brep:
        gp.Constrain( Rhino.DocObjects.ObjRef(surface_id).Surface(), False)
    elif type == Rhino.DocObjects.ObjectType.Mesh:
        gp.Constrain( Rhino.DocObjects.ObjRef(surface_id).Mesh(), False)
    gp.SetCommandPrompt("Set circle center point")
    gp.DynamicDraw += dynamic_draw_curve
    circles = []
    while gp.Get()!= Rhino.Input.GetResult.Cancel:
        if gp.CommandResult() != Rhino.Commands.Result.Success:
            return None
        if gp.Result() != Rhino.Input.GetResult.Option:
            point = gp.Point()
            active_diameter = dbl_option_active_diameter.CurrentValue
            offset = dbl_option_offset.CurrentValue
            circle = circle_on_surface(point, surface_id, active_diameter)
            circle_offset = circle_on_surface(point, surface_id, active_diameter + 2*offset)
            circle_id        = doc.Objects.AddCircle(circle)
            circle_offset_id = doc.Objects.AddCircle(circle_offset)
            ObjectColor([circle_id], syscolor.Blue)
            ObjectColor([circle_offset_id], syscolor.Beige)
            circles.append((circle_id, circle_offset_id))
        if gp.Result() == Rhino.Input.GetResult.Option:
            sticky["cirle_on_surface_active_diameter"] = dbl_option_active_diameter.CurrentValue
            sticky["cirle_on_surface_offset"] = dbl_option_offset.CurrentValue
            gp.Tag["active_diameter"] = dbl_option_active_diameter.CurrentValue
            gp.Tag["offset"] = dbl_option_offset.CurrentValue

if __name__ == "__main__":
    result = select_surface()
    if result:
        base_object = result[1]
        circles = set_circle_on_surface(base_object)
