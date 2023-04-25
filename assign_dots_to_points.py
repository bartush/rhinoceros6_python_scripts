
import rhinoscriptsyntax as rs
import System.Drawing.Color as syscolor


def SelectTextDots():
    rs.UnselectAllObjects()
    command = ""   
    command += "-_SelDot "
    command += " Color"
    command += " Enter "
    rs.Command(command, False)
    return rs.SelectedObjects()

def SelectColorPoints(color):
    rs.UnselectAllObjects()
    command = ""   
    command += "-_SelColor "
    command += " Color"
    command += " "
    command += color
    command += " Enter "
    rs.Command(command, False)
    selected_objects = rs.SelectedObjects()
    point_list = []
    for obj in selected_objects: 
       if not rs.IsPoint(obj): rs.UnselectObject(obj)
       else: point_list.append(obj)
    rs.UnselectAllObjects()
    return point_list


if __name__ == "__main__":
    points = SelectColorPoints("Blue")
    if points != None:
     for point in points: 
       textdot = rs.AddTextDot("d1.7", rs.PointCoordinates(point))
       rs.ObjectColor(textdot, syscolor.White)
    text_dots = SelectTextDots()
    #---- rename text dots
    if text_dots != None:
      for dot in text_dots:
          rs.ObjectName(dot, rs.TextDotText(dot))
          point = rs.AddPoint(rs.TextDotPoint(dot))
    rs.UnselectAllObjects()
