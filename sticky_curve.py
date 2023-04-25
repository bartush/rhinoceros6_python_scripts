import Rhino
from scriptcontext import doc, sticky
import rhinoscriptsyntax as rs
import System.Drawing.Color as syscolor
from System import IntPtr
import System.Collections.Generic.IEnumerable as IEnumerable
from System.Collections.Generic import List
#from System.Media import SoundPlayer

#def sound():
#    sp = SoundPlayer()
#    sp.SoundLocation = "sounds/goutte.wav"
#    sp.Play()
#    #a = raw_input("set number")
#    #print(a)

class StickyCurve(object):
    curve_knot_style = Rhino.Geometry.CurveKnotStyle.Chord
    def __init__(self):
        self.__curve = None
        self.__curve_id = None
        self.__base_surface = None
        self.__base_surface_id = None
        self.__curve_points = []
    def get_curve_points(self):
        return self.__curve_points
    def get_curve(self):
        return self.__curve
    def get_curve_id(self):
        return self.__curve_id
    def get_surf(self):
        return self.__base_surface
    def set_surf(self):
        self.__init__() # as you setting new base surface object must be reinitialised
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
            surf = go.Object(0).Surface()
            self.__base_surface = surf
        elif type == Rhino.DocObjects.ObjectType.Mesh:
            mesh = go.Object(0).Mesh()
            self.__base_surface = mesh
        self.__base_surface_id = go.Object(0).ObjectId
    def pull_curve(self):
        srf_id = self.__base_surface_id
        type = Rhino.DocObjects.ObjRef(srf_id).Object().ObjectType
        if type == Rhino.DocObjects.ObjectType.Mesh:
            pulled_crvs = self.__curve.PullToMesh(Rhino.DocObjects.ObjRef(srf_id).Mesh(), doc.ModelAbsoluteTolerance)
            self.__curve = pulled_crvs
        elif type == Rhino.DocObjects.ObjectType.Brep:
            brep_face = Rhino.DocObjects.ObjRef(srf_id).Brep().Faces[0]
            pulled_crvs = self.__curve.PullToBrepFace(brep_face, doc.ModelAbsoluteTolerance)
            self.__curve = pulled_crvs[0]
    def set_curve(self):
        rs.UnselectAllObjects()
        if self.__base_surface == None: return None
        #print elf.__base_surface
        def dynamic_draw_curve(sender, args):
            points = list(self.__curve_points)
            points.append(args.CurrentPoint)
            # create an display dinamic curve
            dynamic_curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(points, 3, self.curve_knot_style)
            args.Display.DrawCurve(dynamic_curve, syscolor.HotPink, 3)
            # mark all curve points
            for i in range(len(points)):
                args.Display.DrawPoint(points[i], syscolor.HotPink)
                #args.Display.Draw2dText(text, syscolor.Green, text_point, True)
        self.__cure = None
        self.__curve_points = []
        self.__current_point_index = 0
        tag = []
        tag.append(self.__current_point_index)
        gp = Rhino.Input.Custom.GetPoint()
        gp.AcceptUndo(True)
        gp.EnableTransparentCommands(True)
        gp.Constrain(self.__base_surface, True)
        gp.SetCommandPrompt("Select point on surface")
        gp.DynamicDraw += dynamic_draw_curve
        while gp.Get()!= Rhino.Input.GetResult.Cancel:
            if gp.CommandResult()!=Rhino.Commands.Result.Success:
                return gp.CommandResult()
            if gp.Result() != Rhino.Input.GetResult.Option:
                #sound()
                point = gp.Point()
                self.__curve_points.append(point)
                self.__current_point_index += 1
        # create curve - Rhino.Geometry object
        if (len(self.__curve_points) > 1):
            self.__curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(self.__curve_points, 3, self.curve_knot_style)
            self.pull_curve()
            return self.__curve
        else: 
            print("No points selected")
            return None
    def display_curve(self):
        self.__curve_id = doc.Objects.AddCurve(self.__curve)
        doc.Views.Redraw()
    def hide_curve(self):
        if self.__curve_id != None:
            doc.Objects.Delete(self.__curve_id, True)
            doc.Views.Redraw()
            self.__curve_id = None
    def edit_curve(self):
        def dynamic_draw_curve(sender, args):
            points = list(self.__curve_points)
            #points.append(args.CurrentPoint)
            temp_point_id = args.Source.Tag
            points[temp_point_id] = args.CurrentPoint
            # create an display dinamic curve
            dynamic_curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(points, 3, self.curve_knot_style)
            args.Display.DrawCurve(dynamic_curve, syscolor.HotPink, 3)
            # mark all curve points
            for i in range(len(points)):
                args.Display.DrawPoint(points[i], syscolor.HotPink)
                #args.Display.Draw2dText(text, syscolor.Green, text_point, True)
        # loop for point editing
        while True:
            self.hide_curve()
            edit_points_id = []
            for point in self.__curve_points:
                edit_points_id.append(doc.Objects.AddPoint(point))
            doc.Views.Redraw()
            old_p = Rhino.Input.Custom.GetObject()
            old_p.SetCommandPrompt("Select point to edit")
            old_p.GeometryFilter = Rhino.DocObjects.ObjectType.Point
            old_p.SubObjectSelect = False
            old_p.ChooseOneQuestion = True
            old_p.DeselectAllBeforePostSelect = True
            old_p.OneByOnePostSelect = True
            temp_curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(self.__curve_points, 3, self.curve_knot_style)
            temp_curve_id = doc.Objects.AddCurve(self.__curve)
            doc.Views.Redraw()
            old_p.GetMultiple(1,1)
            if old_p.CommandResult()== Rhino.Commands.Result.Cancel:
                for point in edit_points_id:
                    doc.Objects.Delete(point, True)
                doc.Objects.Delete(temp_curve_id, True)
                doc.Views.Redraw()
                break
            if old_p.CommandResult()== Rhino.Commands.Result.Success:
                #sound()
                temp_point_id = old_p.Object(0).ObjectId
                temp_point_index = edit_points_id.index(temp_point_id)
            doc.Objects.Delete(temp_curve_id, True)
            doc.Views.Redraw()
            new_p = Rhino.Input.Custom.GetPoint()
            new_p.Tag = temp_point_index
            new_p.SetCommandPrompt("Select new location")
            new_p.EnableTransparentCommands(True)
            new_p.Constrain(self.__base_surface, True)
            new_p.DynamicDraw += dynamic_draw_curve
            new_p.Get()
            if new_p.CommandResult()== Rhino.Commands.Result.Cancel:
                for point in edit_points_id:
                    doc.Objects.Delete(point, True)
                doc.Objects.Delete(temp_curve_id, True)
                doc.Views.Redraw()
                break
            if new_p.CommandResult()== Rhino.Commands.Result.Success:
                #sound()
                self.__curve_points[temp_point_index] = new_p.Point()
            self.__curve = Rhino.Geometry.Curve.CreateInterpolatedCurve(self.__curve_points, 3, self.curve_knot_style)
            self.pull_curve()
            # delete temp points
            for point in edit_points_id:
                doc.Objects.Delete(point, True)
            doc.Views.Redraw()
            
        return self.__curve
    def create(self, curve_id, points, base_surface_id):
        for point in points:
            self.__curve_points.append(Rhino.Geometry.Point3d(point[0], point[1], point[2]))
        self.__curve    = Rhino.DocObjects.ObjRef(curve_id).Curve()
        self.__curve_id = curve_id
        srf_ref = Rhino.DocObjects.ObjRef(base_surface_id)
        type = srf_ref.Object().ObjectType
        if type == Rhino.DocObjects.ObjectType.Surface or type == Rhino.DocObjects.ObjectType.Brep:
            surf = srf_ref.Surface()
            self.__base_surface = surf
        elif type == Rhino.DocObjects.ObjectType.Mesh:
            mesh = srf_ref.Mesh()
            self.__base_surface = mesh
        self.__base_surface_id = srf_ref.ObjectId
    def archive(self):
        crv_obj = Rhino.DocObjects.ObjRef(self.__curve_id).Object()
        crv_obj.Attributes.UserDictionary.Set("sticky_curve", True)
        crv_obj.Attributes.UserDictionary.Set("base_surface_id", self.__base_surface_id)
        crv_obj.Attributes.UserDictionary.Set.Overloads[str, IEnumerable[float]]("pointsX", map(lambda x: x[0], self.__curve_points))
        crv_obj.Attributes.UserDictionary.Set.Overloads[str, IEnumerable[float]]("pointsY", map(lambda x: x[1], self.__curve_points))
        crv_obj.Attributes.UserDictionary.Set.Overloads[str, IEnumerable[float]]("pointsZ", map(lambda x: x[2], self.__curve_points))

def create_or_edit():
    if sticky.has_key("default_sticky_curve_operation"):
        default_sticky_curve_operation = sticky["default_sticky_curve_operation"]
    else:
        default_sticky_curve_operation = "new"
    gopt = Rhino.Input.Custom.GetOption()
    gopt.SetCommandPrompt("This is Sticky curve, you can create 'new' curve or 'edit' existing")
    gopt.SetCommandPromptDefault(default_sticky_curve_operation)
    opt_list = ["new", "edit", "cancel"]
    for opt in opt_list:
        gopt.AddOption(opt)
    result = gopt.Get()
    if result == Rhino.Input.GetResult.Option:
        current_operation = gopt.OptionIndex()
        if opt_list[current_operation-1] != "cancel":
            sticky["default_sticky_curve_operation"] = opt_list[current_operation-1]
        return opt_list[current_operation-1]
    elif result == Rhino.Input.GetResult.Cancel:
        return default_sticky_curve_operation

def get_sticky_curves_from_doc():
    robjs = doc.Objects.FindByObjectType(Rhino.DocObjects.ObjectType.Curve)
    sticky_curves = []
    for obj in robjs:
        crv = Rhino.DocObjects.ObjRef(obj.Id).Curve()
        if crv.UserDictionary.ContainsKey("sticky_curve"):
            sticky_curves.append(crv.UserDictionary["sticky_curve"])
    return sticky_curves

def start():
    while True:
        action = create_or_edit()
        if action == "cancel":
            break
        if action == "new": # Current Action is Create sticky curve
            crv = StickyCurve()
            crv.set_surf()
            if crv.set_curve() != None:
                crv.display_curve()
                crv.archive()
        if action == "edit": # Current action is Edit sticky curve
            go = Rhino.Input.Custom.GetObject()
            go.SetCommandPrompt("Select sticky curve to edit")
            go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
            go.SubObjectSelect = False
            go.ChooseOneQuestion = True
            go.DeselectAllBeforePostSelect = True
            go.OneByOnePostSelect = True
            go.GetMultiple(1,1) # minmum number = 1, maximum number = 1
            if go.CommandResult() != Rhino.Commands.Result.Success: 
                print("No sticky curve is selected!")
            else: 
                crv_obj = go.Object(0).Object()
                if not crv_obj.Attributes.UserDictionary.ContainsKey("sticky_curve"): 
                    print("Object selected is not sticky curve!")
                else:
                    print("Editing Sticky curve...")
                    curve_id        = go.Object(0).ObjectId
                    base_surface_id = crv_obj.Attributes.UserDictionary["base_surface_id"]
                    points = []
                    pointsX = list(List[float](crv_obj.Attributes.UserDictionary["pointsX"]))
                    pointsY = list(List[float](crv_obj.Attributes.UserDictionary["pointsY"]))
                    pointsZ = list(List[float](crv_obj.Attributes.UserDictionary["pointsZ"]))
                    for index, pointX in enumerate(pointsX):
                        p = Rhino.Geometry.Point3d(pointsX[index], pointsY[index], pointsZ[index])
                        points.append(p)
                    crv = StickyCurve()
                    crv.create(curve_id, points, base_surface_id)
                    if crv.edit_curve() != None:
                        crv.display_curve()
                        crv.archive()

if __name__ == "__main__":
    start()
