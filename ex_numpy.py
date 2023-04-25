    # For now, we need to manually load mtrand before using numpy or scipy
    # I'm still trying to figure out why mtrand is not automatically getting
    # loaded when numpy/scipy imports it.  If I can fix this, we won't need
    # the following two lines
import clr
clr.AddReference("mtrand")

import numpy
import rhinoscriptsyntax as rs

x_coord = [  0,  1,  2,  3,  4,  5,  6]
y_coord = [0.0,0.1,0.5,2.5,2.5,2.5,4.0]
xyz = zip(x_coord,y_coord,[0]*len(x_coord))
rs.AddPoints(xyz)

degree = 5
eq = numpy.polyfit(x_coord, y_coord, degree)
fitfunc = numpy.poly1d(eq)

fit_points = []
for i in range(61):
    x = i/10.0
    y = fitfunc(x)
    fit_points.append((x, y, 0))
rs.AddPolyline(fit_points) 