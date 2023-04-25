# -*- coding: utf-8 -*-

import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc


point_coincedent_tolerance = 0.1
area_tolerance = 10

def FindSymmetryPlane(id):
    def ShowBrepVerts(brep):
        vs = brep.Vertices
        td_list
        for v in vs:
            sc.doc.Objects.AddTextDot(str(v.VertexIndex), v.Location)
        ShowTextDotsFromList(td_list)
    def PlaneBetweenPoints(point1, point2):
        point = point1 + (point2-point1)/2
        return rg.Plane(point, rg.Vector3d(point2-point1))
    def ShowPlane(plane):
        sc.doc.Objects.AddSurface(rg.PlaneSurface(plane, rg.Interval(-1000,1000), rg.Interval(-1000,1000)))
    def IsPlaneInList(plane, lst):
        for p in lst:
            if p.Normal.EpsilonEquals( plane.Normal, point_coincedent_tolerance) or \
               p.Normal.EpsilonEquals(-plane.Normal, point_coincedent_tolerance):
                    return True
                    break
        return False
    def IsSymmetricCentroids(brep1, brep2, plane):
        c1 = rg.AreaMassProperties.Compute(brep1).Centroid
        c2 = rg.AreaMassProperties.Compute(brep2).Centroid
        c2.Transform(rg.Transform.Mirror(plane))
        if c1.EpsilonEquals(c2, point_coincedent_tolerance):
            return True
        return False
 
    brep = Rhino.DocObjects.ObjRef(id).Brep()
    verts = brep.Vertices
    count = verts.Count
    symmetry_planes = []
    if count >= 2:
        for i in range(count):
            #if symmetry_planes != []: break
            for j in range(count):
                if i != j:
                    plane = PlaneBetweenPoints(verts[i].Location, verts[j].Location)
                    crvs = Rhino.Geometry.Intersect.Intersection.BrepPlane(brep, plane, 0.005)[1]
                    brep_pieces = brep.Faces[0].Split(crvs, 0.005)
                    if brep_pieces.Faces.Count == 2:
                        area1 = rg.AreaMassProperties.Compute(brep_pieces.Faces[0]).Area
                        area2 = rg.AreaMassProperties.Compute(brep_pieces.Faces[1]).Area
                        if abs(area1 - area2) <= area_tolerance and \
                           IsSymmetricCentroids(brep_pieces.Faces[0], brep_pieces.Faces[1], plane):
                            if not IsPlaneInList(plane, symmetry_planes):
                                symmetry_planes.append(plane)
                            #break
    #print symmetry_plane
    print "Количество плоскостей симметрии:", len(symmetry_planes)
    if symmetry_planes != []: 
        for p in symmetry_planes:
            ShowPlane(p)
            pass
    #ShowBrepVerts(brep)
    return symmetry_planes

if __name__ == "__main__":
    filter = Rhino.DocObjects.ObjectType.Surface
    rc, objref = Rhino.Input.RhinoGet.GetOneObject("Выберете поверхность для поиска симметрии", False, filter)
    if not objref or rc!=Rhino.Commands.Result.Success: print "Поверхность не выбрана!"
    else: FindSymmetryPlane(objref.ObjectId)