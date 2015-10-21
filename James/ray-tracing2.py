import Image
import sys
from math import sqrt

imagex = 3000
imagey = 3000
x0 = -1.0
x1 = 2.0
y0 = -1.0
y1 = 2.0

radius = 0.02

lights = [(0.00, 0.00, 1.00),
          (0.01, 0.00, 1.00),
          (0.01, 0.01, 1.00),
          (0.00, 0.01, 1.00),
          (0.02, 0.00, 1.00),
          (0.02, 0.01, 1.00),
          (0.00, 0.02, 1.00),
          (0.01, 0.02, 1.00)]
          
# intensity_per_light = 255 / length(lights)

# convert a point from floating point coordinates to image coordinates
def convert_point(pt):
    x = int( (pt[0] - x0)*imagex/(x1-x0) )
    y = int( (y1 - pt[1])*imagey/(y1-y0) )
    if 0 <= x < imagex and 0 <= y < imagey:
        return (x,y)
    else:
        return None

def cast_shadow(pix, light, point, radius):
    if point[2]+radius >= light[2]: #this is the case where a hyperbolic shadow
        return                      #is cast. handle this later
    #elliptical shadow:
    d = [point[0]-light[0], point[1]-light[1], point[2]-light[2]]
    L_sqrd = d[0]**2 + d[1]**2 + d[2]**2
    ldotl = light[0]**2 + light[1]**2 + light[2]**2
    ddotl = d[0]*light[0] + d[1]*light[1] + d[2]*light[2]
    print point,' ',L_sqrd,' ',ldotl,' ',ddotl,' ',radius
    a = d[1]**2 - L_sqrd + radius**2
    b_base = -2*d[1]*ddotl + 2*light[1]*(L_sqrd - radius**2)
    c_base = ddotl**2 - ldotl*(L_sqrd - radius**2)
    b_co1 = 2*d[0]*d[1]
    c_co1 = -2*d[0]*ddotl + 2*light[0]*(L_sqrd - radius**2)
    c_co2 = d[0]**2 - L_sqrd + radius**2
    drawn = False
    det_never_pos = True
    for pt_x in xrange(0, imagex):
        x = x0 + (x1-x0)*(float(pt_x)+0.5)/float(imagex)
        b = b_base + x*b_co1
        c = c_base + x*c_co1 + (x**2)*c_co2
        det = b**2 - 4*a*c
        if det >= 0:
            det_never_pos = False
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
            for pt_y in xrange(pt_y_high, pt_y_low+1):
                pix[pt_x,pt_y] = 0
                drawn = True
            # print pt_y_high, pt_y_low, range(pt_y_high, pt_y_low+1)
    if drawn:
        print "shadow drawn"
    else:
        print "shadow not drawn, det_never_pos: ",det_never_pos
    
def main(infile, outfile):
    strands = []
    f = open(infile,'r')
    while True:
        line = f.readline()
        if line == '\n' or line == '':
            break
        strands.append([])
        while not (line == '\n' or line == ''):
            strands[-1].append( [float(x) for x in line.split(',')] )
            line = f.readline()
    f.close()
    print '%d stands found in file'%len(strands)
    
    ims = [] #one image for each light
    
    for light in lights:
        im = Image.new('L', (imagex, imagey), "white")
        pix = im.load()
        for strand in strands:
            for point in strand:
                cast_shadow(pix, light, point, radius)
        ims.append(im)
    
    if len(ims) != 0:
        im = Image.new('L', (imagex, imagey), "white")
        pix = im.load()
        pixs = [i.load() for i in ims]
        for x in xrange(0,imagex):
            for y in xrange(0,imagey):
                acc = 0
                for p in pixs:
                    acc += p[x,y]
                pix[x,y] = int( float(acc)/float(len(ims)) )
        im.save(outfile, 'JPEG', quality=95)
    # ims[0].save(outfile, 'JPEG', quality=95)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: python ray-tracing2.py <infile> <outfile>'
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
