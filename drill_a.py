
import Rhino
import math
import scriptcontext
from scriptcontext import sticky
import System.Drawing.Color
import rhinoscriptsyntax as rs
import random
import threading
import Rhino.Geometry as rg
import scriptcontext as sc


##################################################################


#----------------------global vars
base_color = System.Drawing.Color.FromArgb(255,255,255,255)
pink_color = System.Drawing.Color.FromArgb(255,255,100,150)

#-----------------------------------


def AddBlockDefinition(object_ids, block_name, base_point=[0,0,0], description=None, URL_description=None, URL=None, replace_block=False, keep_objects=False):
    """ Turns a list of objects into a block definition.
    This script batches the Rhino Command.
    - Scripted by Martin Manegold for imagine -
    Parameters:
      object_ids = list of object IDs (Guids)
      block_name = the name for the new block Definition
      base_point[op] = base point of the new block
      description[opt] = the description of the block.
      URL_description[opt] = the URL description of the block.
      URL[opt] = the URL of the block.     
      replace_block[opt] = if true an existing block with the same name is replaced
      keep_objects[opt] = if true the input objects are kept
     Returns:
      the name of the block definition
      None on Error   
     """
    #Check if the block already exists
    if rs.IsBlock(block_name) and not replace_block:
        #The block already exists
        return block_name
    #Make sure the current clane is the world CPlane
    CPlane_store = rs.ViewCPlane()
    rs.ViewCPlane(rs.CurrentView(), rs.WorldXYPlane())
    base_point = rs.coerce3dpoint(base_point)
    #Select the Objects
    rs.UnselectAllObjects()
    if keep_objects:
        object_ids = rs.CopyObjects(object_ids)
    rs.SelectObjects(object_ids)
    #Initialize command
    command = ""   
    #Start command
    command += "-_block "
    #Add Base Point   
    command += "%d,%d,%d " %(base_point.X, base_point.Y, base_point.Z)
    #Add block name
    command += block_name + " "
    #Check if the block needs to be replaced
    if rs.IsBlock(block_name):
        command += "y "       
    #Add block description
    if description:
        command += "\" %s\" " % (description)
    else:
        command += "_Enter "
    #Block URL Description
    if URL_description:
        command += "\" %s\" " % (URL_description)
    else:
        command += "_Enter "
    #Block URL
    if URL:
        command += "\" %s\" " % (URL)
    else:
        command += "_Enter "
    #Execute command
    rs.Command(command, False)
    #Get the last created objects
    created_objects = rs.LastCreatedObjects()
    #Delete block instance
    rs.DeleteObject(created_objects[2])
    #Make sure the current Clane is the World CPlane
    rs.ViewCPlane(rs.CurrentView(), CPlane_store)
    rs.UnselectAllObjects()
    return block_name

def vectorNormilise3D(vector):
    r = math.sqrt(vector[0]*vector[0] + vector[1]*vector[1] + vector[2]*vector[2])
    return [vector[0]/r, vector[1]/r, vector[2]/r]

def vectorReverse3D(vector):
    return [-vector[0], -vector[1], -vector[2]]

def circleOnSurface(center_point, surface, diameter):
  uv1 = rs.SurfaceClosestPoint(surface, center_point)
  normal_vector = rs.SurfaceNormal(surface, uv1)
  n = vectorNormilise3D(normal_vector)
  nPlane = rs.PlaneFromNormal(center_point, n)
  return Rhino.Geometry.Circle(nPlane, diameter/2)

def CreateDrillBlock(block_name, drill_size, drill_type, color):
   rs.EnableRedraw(False)
   drill_size1 = drill_size #+ 0.05
   ############### name of the block ###################
   if not rs.IsBlock(block_name):
      if drill_type == "default": ######### default drill type
         ################ drill contour ######################
         contour_points = []
         contour_points.append([0.00           , 0, -0.6*drill_size1])
         contour_points.append([0.35*drill_size1, 0, -0.4*drill_size1])
         contour_points.append([0.35*drill_size1, 0, -0.3*drill_size1])
         contour_points.append([0.50*drill_size1, 0, -0.18*drill_size1])
         contour_points.append([0.50*drill_size1, 0,  0.35*drill_size1])
         contour_points.append([0.00*drill_size1, 0,  0.50*drill_size1])
         contour_curve_XZ = rs.AddPolyline(contour_points)
      if drill_type == "norundist": ######### no rundist drill type
         ################ drill contour ######################
         contour_points = []
         contour_points.append([0.00           , 0, (-0.6+0.16)*drill_size1])
         contour_points.append([0.35*drill_size1, 0, (-0.4+0.16)*drill_size1])
         contour_points.append([0.35*drill_size1, 0, (-0.3+0.16)*drill_size1])
         contour_points.append([0.50*drill_size1, 0, (-0.18+0.2)*drill_size1])
         contour_points.append([0.50*drill_size1, 0, ( 0.35+0.16)*drill_size1])
         contour_points.append([0.00*drill_size1, 0,  (0.50+0.16)*drill_size1])
         contour_curve_XZ = rs.AddPolyline(contour_points)
      if drill_type == "through": ######### through drill type
         ################ drill contour ######################
         contour_points = []
         contour_points.append([0.00           , 0, -1.40*drill_size1])
         contour_points.append([0.3*drill_size1, 0, -1.40*drill_size1])
         contour_points.append([0.3*drill_size1, 0, -0.35*drill_size1])
         contour_points.append([0.50*drill_size1, 0, -0.2*drill_size1])
         contour_points.append([0.50*drill_size1, 0,  0.35*drill_size1])
         contour_points.append([0.00*drill_size1, 0,  0.50*drill_size1])
         contour_curve_XZ = rs.AddPolyline(contour_points)
      if drill_type == "corner": ######### corner drill type
         drill_size1 *= 0.45
         ################ drill contour ######################
         #contour_points = []
         #contour_points.append([0.00           , 0,  -0.4*drill_size1])
         #contour_points.append([0.3*drill_size1, 0,  -0.4*drill_size1])
         #contour_points.append([0.5*drill_size1, 0,  -0.15*drill_size1])
         #contour_points.append([0.4*drill_size1, 0,  0.7*drill_size1])
         #contour_points.append([0.00*drill_size1, 0, 0.7*drill_size1])
         #contour_curve_XZ = rs.AddPolyline(contour_points)
         
         contour_points = []
         contour_points.append([0.00           , 0,  -0.4*drill_size1])
         contour_points.append([0.4*drill_size1, 0,  -0.4*drill_size1])
         contour_points.append([0.57*drill_size1, 0,  -0.08*drill_size1])
         contour_points.append([0.35*drill_size1, 0,  0.75*drill_size1])
         contour_points.append([0.00*drill_size1, 0, 0.75*drill_size1])
         
         contour_curve_XZ = rs.AddCurve(contour_points, 3)
      ################ creating revolution surface ################
      axis = rs.AddLine((0,0,0), (0,0,1))
      drill_srf = rs.AddRevSrf(contour_curve_XZ, axis)
      rs.SurfaceIsocurveDensity(drill_srf,-1) # turning off surface isocurves
      ################ deleting temporary geometry #################
      rs.DeleteObject(contour_curve_XZ)
      rs.DeleteObject(axis)
      ################ aplying color to surface ##################
      material_index = rs.AddMaterialToObject(drill_srf)
      rs.MaterialReflectiveColor(material_index, pink_color)
      rs.MaterialColor(material_index,color)
      rs.MaterialName(material_index, "default")
      rs.MaterialShine(material_index, 25)
      rs.MaterialTransparency(material_index, 0)
      ############### creating text dot identifier #################
      if drill_type != "corner":
        td = rg.TextDot("%.2f" % drill_size, rg.Point3d(0,0,0))
        td.FontHeight = 9
        textDot = sc.doc.Objects.AddTextDot(td)
        rs.ObjectName(textDot, "%.2f" % drill_size)
        rs.ObjectColor(textDot, color)
      ################## creating block ############################
      new_objects_list = []
      new_objects_list.append(drill_srf)
      if drill_type != "corner": 
        new_objects_list.append(textDot) 
      else:
        tmp_point = rs.AddPoint(0,0,0)
        new_objects_list.append(tmp_point)
      AddBlockDefinition(new_objects_list, block_name, (0,0,0), description=None, URL_description=None, URL=None, replace_block=True, keep_objects=False)
      created_objects = rs.LastCreatedObjects()
      rs.DeleteObject(created_objects[1])
   rs.EnableRedraw(True)

def drillDraw(drill_center_point, normal_vector, drill_size, drill_type, drill_color):
   n = vectorNormilise3D(normal_vector)
   nPlane = rs.PlaneFromNormal(drill_center_point, n)
   wPlane = rs.PlaneFromNormal([0,0,0],[0,0,1])
   w_to_n = rs.XformRotation1(wPlane, nPlane)
   #color_string = drill_color.ToString()
   color_hex_code = hex(drill_color.A) + hex(drill_color.R) + hex(drill_color.G) + hex(drill_color.B)
   new_block_name = drill_type + "%.2f" % drill_size + "_" + color_hex_code 
   if not rs.IsBlock(new_block_name):
     CreateDrillBlock(new_block_name, drill_size = drill_size, drill_type = drill_type, color = drill_color)
   rs.InsertBlock2(new_block_name, w_to_n)

def CustomMouseMove(sender, args):
    old_point = args.Source.Tag[2]
    if args.ControlKeyDown:
        if args.WindowPoint.Y > old_point.Y: args.Source.Tag[1] -= 0.05
        else: args.Source.Tag[1] += 0.05
            
    args.Source.Tag[2] = args.WindowPoint

def DynamicDrawFunc( sender, args ):
    local_activeDiameter = args.Source.Tag[1]
    if args.Source.Tag[5] == "corner": local_activeDiameter *= 0.43
    local_surface1 = args.Source.Tag[0]
    point = args.CurrentPoint
    circle = circleOnSurface(point, local_surface1, local_activeDiameter)
    if args.Source.Tag[5] != "corner":
        circle1 = circleOnSurface(point, local_surface1, local_activeDiameter+0.3)
        text = "%.2f" % local_activeDiameter 
        args.Display.DrawCircle(circle1, pink_color, 1)
    else: 
        text = "%.2f" % local_activeDiameter
    args.Display.DrawCircle(circle, pink_color, 3)
    previous_text_position_angle = args.Source.Tag[3]
    
    ######## rotating text around center of circle #################
    prev_point = args.Source.Tag[4]
    if args.CurrentPoint != prev_point: angle_increment = 2
    else: angle_increment = 0
    radius_of_rotation = 0.4*args.Source.Tag[1]
    text_position_angle = previous_text_position_angle + angle_increment
    text_point = point
    text_point.X += radius_of_rotation*math.sin(math.radians(text_position_angle))
    text_point.Y += radius_of_rotation*math.cos(math.radians(text_position_angle))
    args.Display.Draw2dText(text, System.Drawing.Color.Green, text_point, True)
    args.Source.Tag[3] = text_position_angle
    

def OrientOnSurface():
    gs = Rhino.Input.Custom.GetObject()
    gs.SetCommandPrompt("Surface to orient on")
    gs.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    gs.SubObjectSelect = True
    gs.DeselectAllBeforePostSelect = False
    gs.OneByOnePostSelect = True
    gs.GetMultiple(1, 1)
    if gs.CommandResult()!= Rhino.Commands.Result.Success: 
        return gs.CommandResult()
    objref = gs.Object(0)
    # get selected surface object
    obj = objref.Object()
    if not obj: return Rhino.Commands.Result.Failure
    # get selected surface (face)
    surface = objref.Surface()
    if not surface: return Rhino.Commands.Result.Failure
    # Unselect surface
    obj.Select(False)
    gp = Rhino.Input.Custom.GetPoint()
    #---------- tags = [activeDiameter, surface]
    default_color = base_color
    default_color_str = "red"
    if not sticky.has_key('diameter'):
        activeDiameter = 1
    else:
        activeDiameter = sticky['diameter']
    WindowPoint = 0
    PreviousPoint = 0
    text_position_angle = 0
    if sticky.has_key("drill_type"):
        drill_type = sticky["drill_type"]
    else:
        drill_type = "default"
    tags = []
    tags.append(surface)
    tags.append(activeDiameter)
    tags.append(WindowPoint)
    tags.append(text_position_angle)
    tags.append(PreviousPoint)
    tags.append(drill_type)
    gp.Tag = list(tags)

    opt_drill_type = ["default", "norundist", "through", "corner"]
    opt = gp.AddOptionList("drillType", opt_drill_type, opt_drill_type.index(drill_type))

    dblOption_activeDiameter = Rhino.Input.Custom.OptionDouble(1)
    opt = gp.AddOptionDouble("Diameter", dblOption_activeDiameter)
    opt_color = Rhino.Input.Custom.OptionColor(default_color)
    gp.AddOptionColor("color", opt_color)
    gp.AcceptUndo(True)
    gp.EnableTransparentCommands(True)
    gp.SetCommandPrompt("Select point on surface")
    gp.DynamicDraw += DynamicDrawFunc
    gp.MouseMove += CustomMouseMove
    gp.Constrain(surface, True)
    gp.AcceptUndo(True)
    
    cd = Rhino.Display.CustomDisplay(True)
    x_coord = 0
    y_coord = 0
    z_coord = 0
    angle = 0
    while gp.Get()!= Rhino.Input.GetResult.Cancel:
        angle += 0.1
        x_coord = math.sin(angle) 
        y_coord = math.cos(angle)
        z_coord = 0.5*angle
        cd.AddPoint(Rhino.Geometry.Point3d(x_coord, y_coord, z_coord), pink_color)
        if gp.CommandResult()!=Rhino.Commands.Result.Success:
            return gp.CommandResult()
        if gp.Result() != Rhino.Input.GetResult.Option  and gp.Result() != Rhino.Input.GetResult.Undo:
            point = gp.Point()
            uv1 = rs.SurfaceClosestPoint(surface, point)
            n1= rs.SurfaceNormal(surface, uv1)
            dblOption_activeDiameter.CurrentValue = gp.Tag[1]
            sticky['diameter'] = gp.Tag[1]
            if gp.Tag[1] != dblOption_activeDiameter.CurrentValue:
                print "fuck"
            default_color = opt_color.CurrentValue
            activeDiameter = gp.Tag[1]
            scriptcontext.doc.Views.Redraw()
            drillDraw(point, n1, activeDiameter, drill_type, default_color)
        if gp.Result() == Rhino.Input.GetResult.Option:
            list_index = gp.Option().CurrentListOptionIndex
            if list_index >= 0: 
                drill_type = opt_drill_type[list_index]
                gp.Tag[5] = drill_type
                sticky["drill_type"] = drill_type
            gp.Tag[1] = dblOption_activeDiameter.CurrentValue
            
            sticky['diameter'] = gp.Tag[1]
        if gp.Result() == Rhino.Input.GetResult.Undo:
            print "Undo is not working this time! Sorry! :("
    ######  dispose custom display object  #####
    cd.Dispose()
if __name__ == "__main__":
    OrientOnSurface()