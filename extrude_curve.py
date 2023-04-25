import Rhino
import System.Drawing.Color
import scriptcontext
 
def draw_extrusion():
    rc, objref = Rhino.Input.RhinoGet.GetOneObject("Base curve", False, Rhino.DocObjects.ObjectType.Curve)
    if rc!=Rhino.Commands.Result.Success: return
    curve = objref.Curve()
    if not curve: return
 
    # Color to use when drawing dynamic lines
    line_color = System.Drawing.Color.Black
    pt_start = curve.GetBoundingBox(False).Center
 
    # This is a function that is called whenever the GetPoint's
    # DynamicDraw event occurs
    def GetPointDynamicDrawFunc( sender, args ):
        #draw a line from the first picked point to the current mouse point
        args.Display.DrawLine(pt_start, args.CurrentPoint, line_color, 2)
        vector = args.CurrentPoint - pt_start
        extrusion = Rhino.Geometry.Surface.CreateExtrusion(curve,vector)
        if extrusion:
            args.Display.DrawSurface(extrusion, line_color, 1)
            extrusion.Dispose()
 
    # Create an instance of a GetPoint class and add a delegate
    # for the DynamicDraw event
    gp = Rhino.Input.Custom.GetPoint()
    gp.DynamicDraw += GetPointDynamicDrawFunc
    gp.Get()
    if( gp.CommandResult() == Rhino.Commands.Result.Success ):
        vector = gp.Point() - pt_start
        extrusion = Rhino.Geometry.Surface.CreateExtrusion(curve,vector)
        if extrusion:
            scriptcontext.doc.Objects.AddSurface(extrusion)
            scriptcontext.doc.Views.Redraw()
 
 
if( __name__ == "__main__" ):
    draw_extrusion() 