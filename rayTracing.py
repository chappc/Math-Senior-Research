import Image
import sys
from math import sqrt
from ADParser import parse_file
from time import time

# convert a point from floating point coordinates to image coordinates
def convert_point(pt):
    x = int(round( (pt[0] - x0)*imagex/(x1-x0) ))
    y = int(round( (y1 - pt[1])*imagey/(y1-y0) ))
    if 0 <= x < imagex and 0 <= y < imagey:
        return (x,y)
    else:
        return None

def cast_shadow_cylinder(pix, light, point1, point2, radius, region, resolution):
    pass

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
    for pt_x in xrange(0, imagex):
        x = x0 + (x1-x0)*(float(pt_x)+0.5)/float(imagex)
        b = b_base + x*b_co1
        c = c_base + x*c_co1 + (x**2)*c_co2
        det = b**2 - 4*a*c
        if det >= 0:
            sqrt_det_over_2a = sqrt(det)/(2*a)
            vertex = -b/(2*a)
            y_low  = vertex - sqrt_det_over_2a
            y_high = vertex + sqrt_det_over_2a
            if y_low > y_high:
                y_low, y_high = y_high, y_low
            if y_low > y1 or y_high < y0:
                continue
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
    
def main(infile, outfile):
    lights, radius, region, resolution, strands = parse_file(infile)
    x0,x1,y0,y1 = region
    imagex,imagey = resolution
    
    if not bool(lights):
        print "No lights found in the input file."
        quit()
    
    ims = [] #one image for each light
    
    t1 = time()
    
    for light in lights:
        im = Image.new('L', (imagex, imagey), "white")
        pix = im.load()
        for strand in strands:
            for point in strand:
                cast_shadow_sphere(pix, light, point, radius, region, resolution)
            for i in xrange(len(strand)-1):
                point1 = strand[i]
                point2 = strand[i+1]
                cast_shadow_cylinder(pix, light, point1, point2, radius, region, resolution)
        ims.append(im)
    
    t2 = time()
    
    im = Image.new('L', (imagex, imagey), "white")
    pix = im.load()
    pixs = [i.load() for i in ims]
    for x in xrange(0,imagex):
        for y in xrange(0,imagey):
            acc = 0
            for p in pixs:
                acc += p[x,y]
            pix[x,y] = int( float(acc)/float(len(ims)) )
            
    t3 = time()
    
    im.save(outfile, 'JPEG', quality=95)
    
    t4 = time()
    
    print 'It took',t2-t1,'seconds to draw the shadows for individual lights.'
    print 'It took',t3-t2,'seconds to merge the shadows.'
    print 'It took',t4-t3,'seconds to save the image.'

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: python ray-tracing2.py <infile> <outfile>'
        sys.exit(2)
    main(sys.argv[1], sys.argv[2].strip())