import Image

f = open('art-description.ad','r')

strands = []

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

imagex = 3000
imagey = 3000
x0 = -1.0
x1 = 2.0
y0 = -1.0
y1 = 2.0

# convert a point from floating point coordinates to image coordinates
def convert_point(pt):
    x = int( (pt[0] - x0)*imagex/(x1-x0) )
    y = int( (y1 - pt[1])*imagey/(y1-y0) )
    if 0 <= x < imagex and 0 <= y < imagey:
        return (x,y)
    else:
        return None

im = Image.new('L', (imagex, imagey), "white")
raw = list(im.getdata())
def plot(x,y):
    raw[x+imagex*y] = 0

def sign(x):
    if x >= 0:
        return 1
    else:
        return -1

def draw_line(pt1, pt2):
    pt1 = convert_point(pt1)
    pt2 = convert_point(pt2)
    if pt1 == None or pt2 == None:
        return
    if pt1[0] == pt2[0]: # line is vertical
        if pt1[1] <= pt2[1]:
            r = xrange(pt1[1], pt2[1]+1)
        else:
            r = xrange(pt2[1], pt1[1]+1)
        for y in r:
            plot(pt1[0],y)
    else:
        deltax = float(pt2[0] - pt1[0])
        deltay = float(pt2[1] - pt1[1])
        error = 0.0
        deltaerr = abs( deltay/deltax )
        y = pt1[1]
        if pt1[0] <= pt2[0]:
            r = xrange(pt1[0], pt2[0]+1)
        else:
            r = xrange(pt1[0], pt2[0]-1, -1)
        for x in r:
            plot(x,y)
            error += deltaerr
            while error >= 0.5:
                plot(x,y)
                y += sign(pt2[1]-pt1[1])
                error -= 1.0
    
def draw_shadow(light, endpoint1, endpoint2):
    alpha1 = light[2] / (light[2]-endpoint1[2])
    alpha2 = light[2] / (light[2]-endpoint2[2])
    shadowpt1 = []
    shadowpt2 = []
    shadowpt1.append( light[0] + alpha1*(endpoint1[0] - light[0]) )
    shadowpt1.append( light[1] + alpha1*(endpoint1[1] - light[1]) )
    shadowpt2.append( light[0] + alpha2*(endpoint2[0] - light[0]) )
    shadowpt2.append( light[1] + alpha2*(endpoint2[1] - light[1]) )
    draw_line(shadowpt1, shadowpt2)
    
light_position = [0.0,0.0,1.0]
for strand in strands:
    for i in xrange(0, len(strand)-1):
        draw_shadow(light_position, strand[i], strand[i+1])
        
im.putdata(raw)
im.save("shadow.jpeg", quality=95)# , optimize=True)