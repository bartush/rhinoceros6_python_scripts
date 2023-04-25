import Rhino
import Rhino.Geometry as rg
from scriptcontext import doc, sticky


def SelectNurbsSurface():
    filter = Rhino.DocObjects.ObjectType.Surface
    rc, objref = Rhino.Input.RhinoGet.GetOneObject("Selet surface", False, filter)
    if not objref or rc != Rhino.Commands.Result.Success: 
        print "Surface is not selected!"
        return None
    else:
        return objref.Surface().ToNurbsSurface()

def DuplicateNurbsSurfaceControlPoints(nurbs_surface):
    if nurbs_surface != None:
        for u in range(nurbs_surface.Points.CountU):
            for v in range(nurbs_surface.Points.CountV):
                point = nurbs_surface.Points.GetControlPoint(u, v).Location
                doc.Objects.AddPoint(point)

if __name__ == "__main__":
    try:
        print Rhino.RhinoDoc.ActiveDoc.Name
        DuplicateNurbsSurfaceControlPoints(SelectNurbsSurface())
    except Exception as e:
        print e