import Rhino
import math
import rhinoscriptsyntax as rs

def draw_box(center, width):
    plane = rs.MovePlane(rs.WorldXYPlane(),
        [center[0] - width/2, center[1] - width/2, 0])
    return rs.AddRectangle(plane, width, width)

def draw_symetric_boxes(center, width, voffset):
        draw_box([center[0], center[1] + voffset, 0], width)
        draw_box([-center[0], center[1] + voffset, 0], width)
        draw_box([center[0], -center[1] + voffset, 0], width)
        draw_box([-center[0], -center[1] + voffset, 0], width)

def channel_box_params(xl, xr, r):
    """
    xl an xr are left and right boundaries
    both positive such that xr > xl
    r is raduis of circle
    """
    yl = math.sqrt(r*r-xl*xl)
    yr = math.sqrt(r*r-xr*xr)
    RR = math.sqrt(xr*xr + yl*yl)
    alpha = abs(math.pi.real*0.25 - math.asin(xr/RR))
    sin_gamma = RR * math.sin(alpha)/r
    gamma = abs(math.pi.real - math.asin(sin_gamma))
    beta = math.pi.real - alpha - gamma
    d = math.sqrt(r*r + RR*RR - 2*r*RR*math.cos(beta))
    w = 0.5 * math.sqrt(2) * d
    xc = xr - 0.5 * w
    yc = yl - 0.5 * w
    return [[xc,yc], w]

def divide(xl, xr, radius, threshold, delta):
    r = radius - delta
    yl = math.sqrt(r*r-xl*xl)
    yr = math.sqrt(r*r-xr*xr)
    [[xc, yc,], w] = channel_box_params(xl, xr, r)
    draw_symetric_boxes([xc, yc, 0], w, radius)
    xd = xc - w * 0.5
    yd = yc - w * 0.5
    if (min(abs(xl - xd), abs(yl - yd), abs(xr - xd), abs(yr - yd)) < threshold):
        return
    if (min(abs(xl - xd), abs(yl - yd)) > threshold):
        divide(xl, xd, radius, threshold, delta)
    if (min(abs(xr - xd), abs(yr - yd)) > threshold):
        divide(xd, xr, radius, threshold, delta)

def test1(r):
    n = 10
    for i in range(0, n):
        xl = i * r / n;
        xr = (i + 1) * r / n;
        [[xc, yc,], w] = channel_box_params(xl, xr, r)
        draw_box([xc, yc, 0], w)
        [[xc, yc,], w] = channel_box_params(xl, xr, r)
        draw_box([xc, -yc, 0], w)
        [[xc, yc,], w] = channel_box_params(xl, xr, r)
        draw_box([-xc, -yc, 0], w)
        [[xc, yc,], w] = channel_box_params(xl, xr, r)
        draw_box([-xc, yc, 0], w)

def test2(radius, threshold, delta):
    xl = 0
    r = radius - delta
    xr = radius - delta
    [[xc, yc,],w] = channel_box_params(xl, xr, r)
    #draw_symetric_boxes([xc, yc, 0], w, r)
    while w > threshold:
        [[xc, yc,],w] = channel_box_params(xl, xr, r)
        draw_symetric_boxes([xc, yc, 0], w, radius)
        xr = xc - 0.5 * w

def test3(radius, threshold, delta):
    xl = 0
    xr = radius - delta
    divide(xl, xr, radius, threshold, delta)

if __name__ == "__main__":
    R = 20
    plane = rs.MovePlane(rs.WorldXYPlane(),
        [0, + R, 0])
    rs.AddCircle(plane, R)
    #test1(R)
    threshold = 0.1#R*0.1
    delta = 0#threshold * 0.5
    test3(R, threshold, delta)

