import Image
import sys
from math import sqrt
from ADParser import parse_file
from math import floor

class vector():
    def __init__(self, _x,_y,_z):
        self.x = _x
        self.y = _y
        self.z = _z
    
    @classmethod
    def fromList(cls, list):
        return cls(list[0],list[1],list[2])
    
    def add(self, other):
        return vector(self.x+other.x,
                      self.y+other.y,
                      self.z+other.z)
    
    def subtract(self, other):
        return vector(self.x-other.x,
                      self.y-other.y,
                      self.z-other.z)
    
    def scalar_prod(self,alpha):
        return vector(alpha*self.x,
                      alpha*self.y,
                      alpha*self.z)
    
    def dot_prod(self, other):
        return self.x*other.x+self.y*other.y+self.z*other.z
        
    def length(self):
        return sqrt(self.dot_prod(self))
    
    def distance(self, other):
        return self.subtract(other).length()

def check_inter_sphere(center,radius,light,sample_pt):
    v1 = sample_pt.subtract(light)
    v2 = sample_pt.subtract(center)
    #divisoin by zero could result if sample_pt and light are the same:
    alpha = v1.dot_prod(v2)/v1.dot_prod(v1)
    if alpha > 0:
        if alpha < 1:
            closest = light.scalar_prod(alpha).add(sample_pt.scalar_prod(1-alpha))
        else:
            closest = light
    else:
        closest = sample_pt
    return (center.distance(closest) <= radius)
    
def check_inter_cylinder(center1,center2,radius,light,sample_pt):
    # matrix relation
    # (a b) (alpha) = (e)
    # (c d) (beta )   (f)
    v1 = sample_pt.subtract(light)
    v2 = center2.subtract(center1)
    v3 = sample_pt.subtract(center2)
    a = -v1.dot_prod(v1)
    b =  v1.dot_prod(v2)
    c = -b
    d =  v2.dot_prod(v2)
    e = -v1.dot_prod(v3)
    f = -v2.dot_prod(v3)
    
    #Assume that:
    # a != 0 b/c light and sample_pt are different
    # d != 0 b/c the centers are diffent
    
    dprime = (d - (c/a)*b)
    if dprime == 0: #d*a == c*b, which by Cauchy-Schwarz means that v1 and v2 are linearly dependant
        alpha = 0
        beta = f/d
    else:
        fprime = (f - (c/a)*e)
        beta = fprime/dprime
        alpha = (e - b*beta)/a
    
    if alpha > 0 and alpha < 1:
        if beta > 0 and beta < 1:
            v4 =   light.scalar_prod(alpha).add(sample_pt.scalar_prod(1-alpha))
            v5 = center1.scalar_prod(beta ).add(  center2.scalar_prod(1-beta ))
            return (v4.distance(v5) <= radius)
        else:
            return False
    else: #check_inter_sphere(center,radius,light,sample_pt)
        return ( check_inter_sphere(center1,  radius,light,sample_pt) or
                 check_inter_sphere(center2,  radius,light,sample_pt) or
                 check_inter_sphere(light,    radius,center1,center2) or
                 check_inter_sphere(sample_pt,radius,center1,center2) )
    
def coordinate_magick(light,p,z,radius):
    c = (z-light.z)/(p.z-light.z)
    proj = light.scalar_prod(1-c).add(p.scalar_prod(c))
    return ( int(floor(proj.x/radius)), int(floor(proj.y/radius)) )
    
# cutoffs must be sorted decending
def greatest_index_gtoreq(cutoffs,z,min=0,max=None):
    if max == None:
        max = len(cutoffs)
    if min == max:
        return -1
    if max == min+1:
        if cutoffs[min] >= z:
            return min
        else:
            return -1
    mid = (min+max)/2
    if cutoffs[mid] >= z:
        return greatest_index_gtoreq(cutoffs,z,mid,max)
    else:
        return greatest_index_gtoreq(cutoffs,z,min,mid)
    
def build_ds(light,radius,region,strands):
    # One day we will get rid of this check:
    if 8.0*radius > light.z:
        raise Exception('Haven\'t yet written code to handle large radii/low lights')
    cuts = [c*light.z for c in [0.75,0.50,0.25]]
    ds = [[]] + [(z,{}) for z in cuts]
    cutoffs = [z-radius for z in cuts]
    cutoffs.append(-radius)
    for s in strands:
        for point in s:
            p = vector.fromList(point)
            #at this point there should be code to exclude spheres that do not intersect
            #the rectangular pyramid defined by the light and region
            i = greatest_index_gtoreq(cutoffs,p.z)
            if i == -1:
                ds[0].append(p)
            elif i == len(cutoffs)-1:   
                pass
            else:
                i += 1
                z = ds[i][0]
                coords = coordinate_magick(light,p,z,radius)
                try:
                    ds[i][1][coords].append(p)
                except KeyError:
                    ds[i][1][coords] = [p]
    return ds
    
def check_helper(light,z,dict,radius,sample_pt):
    x,y = coordinate_magick(light,sample_pt,z,radius)
    hit = False
    for coords in [(x+dx,y+dy) for dx in [-1,0,1] for dy in [-1,0,1]]:
        try:
            for center in dict[coords]:
                if check_inter_sphere(center,radius,light,sample_pt):
                    return True
        except KeyError:
            pass
    return False
    
def main(infile, outfile):
    lights, radius, region, resolution, strands = parse_file(infile)
    x0,x1,y0,y1 = region
    imagex,imagey = resolution
    intensity = int( 255.0 / float(len(lights)) )
    print intensity
    
    im = Image.new('L', (imagex, imagey), "white")
    pix = im.load()
    
    done = 0
    for l in lights:
        light = vector.fromList(l)
        ds = build_ds(light,radius,region,strands)
        for x in xrange(imagex):
            s = x0 + (x1-x0)*(float(x)+0.5)/float(imagex)
            for y in xrange(imagey):
                t = y1 - (y1-y0)*(float(y)+0.5)/float(imagey)
                sample_pt = vector(s,t,0.0)
                hit = False
                for center in ds[0]:
                    if check_inter_sphere(center,radius,light,sample_pt):
                        pix[x,y] -= intensity
                        hit = True
                        break
                if hit:
                    done += 1
                    print done,x,y
                    continue
                for (z,dict) in ds[1:]:
                    if check_helper(light,z,dict,radius,sample_pt):
                        pix[x,y] -= intensity
                        hit = True
                        break
                # if hit:
                    # done += 1
                    # print done
                    # continue
                
                # for strand in strands:
                    # for i in xrange(1,len(strand)):
                        # c1 = vector.fromList(strand[i-1])
                        # c2 = vector.fromList(strand[ i ])
                        # if check_inter_cylinder(c1,c2,radius,light,sample_pt):
                            # pix[x,y] -= intensity
                            # hit = True
                            # break
                    # if hit:
                        # break
                done += 1
                print done,x,y
    
    im.save(outfile, 'JPEG', quality=95)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'usage: python ray-tracing2.py <infile> <outfile>'
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
