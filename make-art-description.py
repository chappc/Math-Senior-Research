from math import sin, cos, pi, sqrt

f = open('art-description.ad','w')

f.write('lights section:\n')
lights = [(0.00, 0.00, 1.00),
          (0.01, 0.00, 1.00),
          (0.01, 0.01, 1.00),
          (0.00, 0.01, 1.00),
          (0.02, 0.00, 1.00),
          (0.02, 0.01, 1.00),
          (0.00, 0.02, 1.00),
          (0.01, 0.02, 1.00)]
for light in lights:
  f.write(str(light[0])+', '+str(light[1])+', '+str(light[2])+'\n')
f.write('\n')

f.write('radius= 0.02\n')
f.write('region= -1.0,2.0,-1.0,2.0\n')
f.write('resolution= 3000,3000\n')
f.write('\n')

f.write('strands section:\n')
# Strand one:
for x in [x*0.01 for x in xrange(0,101)]: #xrange(0.0,1.0,0.01):
  f.write( str(x)+', '+str(0.25*sin(3*pi*x))+', '+str(0.45+(0.1*sin(3*pi*x)))+'\n' )
f.write('\n')

# Strand two:
for y in [y*0.01 for y in xrange(0,101)]:
  f.write( '0.0, '+str(y)+', 0.45\n' )
f.write('\n')

# Strand three:
for x in [x*0.01/sqrt(2.0) for x in xrange(0,2+int(100*sqrt(2.0)))]:#xrange(0.0,1.0,0.01/sqrt(2)):
  f.write( str(x)+', '+str(1.0-x)+', 0.45\n' )
f.write('\n')

f.close()