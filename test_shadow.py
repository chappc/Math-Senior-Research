import Image
import sys
from math import sqrt

def cast_shadow_sphere(pix, light, point, radius, region, resolution):
    x0,x1,y0,y1 = region
    imagex,imagey = resolution
    if point[2]+radius >= light[2]: #this is the case where a hyperbolic shadow
        return                      #is cast. handle this later
    #elliptical shadow:
    d = [point[0]-light[0], point[1]-light[1], point[2]-light[2]]
    L_sqrd = d[0]**2 + d[1]**2 + d[2]**2
    ldotl = light[0]**2 + light[1]**2 + light[2]**2
    ddotl = d[0]*light[0] + d[1]*light[1] + d[2]*light[2]
    a = d[1]**2 - L_sqrd + radius**2
    b_base = -2*d[1]*ddotl + 2*light[1]*(L_sqrd - radius**2)
    c_base = ddotl**2 - ldotl*(L_sqrd - radius**2)
    b_co1 = 2*d[0]*d[1]
    c_co1 = -2*d[0]*ddotl + 2*light[0]*(L_sqrd - radius**2)
    c_co2 = d[0]**2 - L_sqrd + radius**2
    # find determinant at the lower edge of the screen
    x = x0 + (x1-x0)*(float(0)+0.5)/float(imagex)
    b = b_base + x*b_co1
    c = c_base + x*c_co1 + (x**2)*c_co2
    detl = b**2 - 4*a*c
    # find determinant at the upper edge of the screen
    x = x0 + (x1-x0)*(float(imagex)-0.5)/float(imagex)
    b = b_base + x*b_co1
    c = c_base + x*c_co1 + (x**2)*c_co2
    detu = b**2 - 4*a*c
    #
    #  ddet/dx = 2*b*(b_co1) - 4*a*(c_co1 + 2*c_co2*x)
    #  = 2*(b_base + b_col*x)*b_co1 - 4*a*(c_co1 + 2*c_co2*x)
    #  = 2*b_base*b_co1 + 2*b_co1**2*x - 4*a*c_co1 - 8*a*c_co2*x
    #  x = (4*a*c_co1 - 2*b_base*b_co1)/(b_co1**2 - 8*a*c_co2)
    #
    xcenter = (4*a*c_co1 - 2*b_base*b_co1)/(b_co1**2 - 8*a*c_co2)
    if detl < 0 and detu < 0 and (xcenter < x0 or xcenter > x1):
        # no portion of the shadow falls on the canvas
        return
    if xcenter < x0:
        xcenter = x0
    elif xcenter > x1:
        xcenter = x1
    pt_xstart = int( (xcenter-x0)*imagex/(x1-x0) - 0.5 )
    #print "  xstart:", pt_xstart
    pt_x = pt_xstart
    x = x0 + (x1-x0)*(float(pt_x)+0.5)/float(imagex)
    b = b_base + x*b_co1
    c = c_base + x*c_co1 + (x**2)*c_co2
    det = b**2 - 4*a*c
    while det >= 0 and pt_x >= 0:
        #print "  At", pt_x, "with det", det
        sqrt_det_over_2a = sqrt(det)/(2*a)
        vertex = -b/(2*a)
        y_low  = vertex - sqrt_det_over_2a
        y_high = vertex + sqrt_det_over_2a
        if y_low > y_high:
            y_low, y_high = y_high, y_low
        if y_low <= y1 and y_high >= y0:
            pt_y_low  = int( (y1 - y_low )*imagey/(y1-y0) )
            if pt_y_low >= imagey:
                pt_y_low = imagey-1
            pt_y_high = int( (y1 - y_high)*imagey/(y1-y0) )
            if pt_y_high >= imagey:
                pt_y_high = imagey-1
            if pt_y_high < 0:
                pt_y_high = 0
            for pt_y in xrange(pt_y_high, pt_y_low+1):
                pix[pt_x,pt_y] = 0
            
        pt_x -= 1
        x = x0 + (x1-x0)*(float(pt_x)+0.5)/float(imagex)
        b = b_base + x*b_co1
        c = c_base + x*c_co1 + (x**2)*c_co2
        det = b**2 - 4*a*c
        
    pt_x = pt_xstart + 1
    x = x0 + (x1-x0)*(float(pt_x)+0.5)/float(imagex)
    b = b_base + x*b_co1
    c = c_base + x*c_co1 + (x**2)*c_co2
    det = b**2 - 4*a*c
    while det >= 0 and pt_x < imagex:
        #print "  At", pt_x, "with det", det
        sqrt_det_over_2a = sqrt(det)/(2*a)
        vertex = -b/(2*a)
        y_low  = vertex - sqrt_det_over_2a
        y_high = vertex + sqrt_det_over_2a
        if y_low > y_high:
            y_low, y_high = y_high, y_low
        if y_low <= y1 and y_high >= y0:
            pt_y_low  = int( (y1 - y_low )*imagey/(y1-y0) )
            if pt_y_low >= imagey:
                pt_y_low = imagey-1
            pt_y_high = int( (y1 - y_high)*imagey/(y1-y0) )
            if pt_y_high >= imagey:
                pt_y_high = imagey-1
            if pt_y_high < 0:
                pt_y_high = 0
            for pt_y in xrange(pt_y_high, pt_y_low+1):
                pix[pt_x,pt_y] = 0
            
        pt_x += 1
        x = x0 + (x1-x0)*(float(pt_x)+0.5)/float(imagex)
        b = b_base + x*b_co1
        c = c_base + x*c_co1 + (x**2)*c_co2
        det = b**2 - 4*a*c
    


if __name__=="__main__":
  
    LIGHT=(0.0,0.0,1.0)
    POINT=(0.15,0.2,0.2)
    RADIUS=0.08
    REGION=(0.0,1.0,0.0,1.0)
    RESOLUTION=(128,128)
  
    pix = [[' ']*128 for x in xrange(128)]
    cast_shadow_sphere(pix,LIGHT,POINT,RADIUS,REGION,RESOLUTION)
    for line in pix:
        print "".join(line)
        