
f = open('grid-of-spheres.ad','w')

# Strand one:
for x in [lx*0.1 for lx in xrange(0,11)]:
    for y in [ly*0.1 for ly in xrange(0,11)]:
        f.write( str(x)+', '+str(y)+', '+str(0.02)+'\n' )
f.write('\n')

f.close()