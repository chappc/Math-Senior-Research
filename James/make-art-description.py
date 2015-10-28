from math import sin, cos, pi, sqrt

f = open('art-description.ad','w')

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