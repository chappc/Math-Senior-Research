
f = open('grid-of-spheres-sparse.ad','w')

# Strand one:
for x in [0.0,0.25,1.0,1.5]:
    for y in [0.0,0.25,1.0,1.5]:
        f.write( str(x)+', '+str(y)+', '+str(0.02)+'\n' )
f.write('\n')

f.close()