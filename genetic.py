import math
import random

# Exponential decay based selection from list
def expon_pair ( lis ):
  lambd = .01 / len(lis) # mean is halfway through list
  # randomly pick an index using exponential decay
  sel1 = int(random.expovariate(lambd))
  # if index too high, pick again
  while sel1 >= len(lis):
    sel1 = int(random.expovariate(lambd))
  # randomly pick second index
  sel2 = int(random.expovariate(lambd))
  # make sure second index is in list and not first index
  while sel2 >= len(lis) or sel2 == sel1:
    sel2 = int(random.expovariate(lambd))
  return (lis[sel1], lis[sel2])

def genetic ( gc, ge, it, cr, mp ):
  # Set up list of genomes
  glist = [gc() for i in xrange(ge)]
  # Run algorithm for it generations
  for i in xrange(it):
    # sort the genomes by fitness
    # also cull all genomes past the cull_rate
    gfit = sorted(glist, key=gc.fitness) [:int(math.ceil(ge * cr))]

    # randomly pick pairs from the survivors and try to mate and produce offspring
    glist = list(sum([gc.mate(expon_pair(gfit), random.uniform(0,1)>mp) for i in xrange(ge/2)], []))

#max_fitness = -float("inf")

if __name__ == "__main__":

  import Tkinter as tk

  root = tk.Tk()
  root.title("Genetic Travelling Salesman")
  maxx = root.winfo_screenwidth() # canvas width, in pixels
  maxy = root.winfo_screenheight() # canvas height, in pixels
  cx = maxx/2 - 400
  cy = maxy/2 + 250
  chart_1 = tk.Canvas(root, width=maxx, height=maxy, background="white")
  chart_1.grid(row=0, column=0)

  towns = [(6734, 1453), (2233, 10), (5530, 1424), (401, 841), (3082, 1644), \
    (7608, 4458), (7573, 3716), (7265, 1268), (6898, 1885), (1112, 2049), \
    (5468, 2606), (5989, 2873), (4706, 2674), (4612, 2035), (6347, 2683), \
    (6107, 669), (7611, 5184), (7462, 3590), (7732, 4723), (5900, 3561), \
    (4483, 3369), (6101, 1110), (5199, 2182), (1633, 2809), (4307, 2322), \
    (675, 1006), (7555, 4819), (7541, 3981), (3177, 756), (7352, 4506), \
    (7545, 2801), (3245, 3305), (6426, 3173), (4608, 1198), (23, 2216), \
    (7248, 3779), (7762, 4595), (7392, 2244), (3484, 2829), (6271, 2135), \
    (4985, 140), (1916, 1569), (7280, 4899), (7509, 3239), (10, 2676), \
    (6807, 2993), (5185, 3258), (3023, 1942)]

  def draw_towns():
    r = 5
    color = "#123456"
    for town in towns:
      bb = (cx+town[0]/10-r,cy-town[1]/10-r,cx+town[0]/10+r,cy-town[1]/10+r)
      chart_1.create_oval(bb, fill=color)


  class Travelling_Salesman():
    def __init__(self, init_list=None):
      if init_list == None:
        order = range(len(towns))
        random.shuffle(order)
        self.nxt = [0]*len(towns)
        for i in xrange(len(towns)):
          self.nxt[order[i-1]] = order[i]
      else:
        self.nxt = init_list
      self.draw()

    def draw(self):
      chart_1.delete(tk.ALL)
      tn = self.nxt[0]
      chart_1.create_line( cx + towns[0][0]/10, cy - towns[0][1]/10, \
                           cx + towns[tn][0]/10, cy - towns[tn][1]/10 )
      while tn != 0:
        tp = tn
        tn = self.nxt[tp]
        chart_1.create_line( cx+towns[tp][0]/10, cy-towns[tp][1]/10, \
                             cx+towns[tn][0]/10, cy-towns[tn][1]/10 )
      draw_towns()
      chart_1.create_text( cx, cy+10, text="Fitness: %.2f" %self.fitness() )
      #\nMax: %.2f" %(self.fitness(), max_fitness) )
      chart_1.update()
      chart_1.after(100)

    def fitness(self):
      tn = self.nxt[0]
      fit = math.sqrt( (towns[0][0]-towns[tn][0])**2 + (towns[0][1]-towns[tn][1])**2 )
      while tn != 0:
        tp = tn
        tn = self.nxt[tp]
        fit -= math.sqrt( (towns[tp][0]-towns[tn][0])**2 + (towns[tp][1]-towns[tn][1])**2 )
        #if fit > max_fitness:
        #  max_fitness = fit
      return fit

    @classmethod
    def mate(cls, par, mut):
      nxt1 = [-1]*len(towns)
      nxt2 = [-1]*len(towns)
      # set of towns in first child with unlinked forward edges
      unlinked_f1 = set(range(len(towns)))
      # set of towns in second child with unlinked back edges
      unlinked_b1 = set(range(len(towns)))
      
      for i in xrange(len(towns)):
        if par[0].nxt[i] == par[1].nxt[i]:
          nxt1[i] = nxt2[i] = par[0].nxt[i]
          unlinked_f1.discard(i)
          unlinked_b1.discard(nxt1[i])
      
      unlinked_f2 = unlinked_f1.copy()
      unlinked_b2 = unlinked_b1.copy()
      
      def test_loop ( nxt, i ):
        p = i
        for k in xrange(len(nxt)):
          p = nxt[p]
          if p == i:
            p = nxt[p]
            print i,
            while p != i:
              print p,
              p = nxt[p]
            print i
            print "---"
            return True
          if p == -1:
            return False
        return False
      
      for i in sorted(list(unlinked_f1)):
        print len(unlinked_f1), len(unlinked_f2)
        s = random.randint(0,1)
        n1 = par[s].nxt[i]
        if n1 in unlinked_b1:
          nxt1[i] = n1
          if test_loop(nxt1, i):
            nxt1[i] = -1
          else:
            unlinked_f1.discard(i)
            unlinked_b1.discard(n1)
        n2 = par[1-s].nxt[i]
        if n2 in unlinked_b2:
          nxt2[i] = n2
          if test_loop(nxt2, i):
            nxt2[i] = -1
          else:
            unlinked_f2.discard(i)
            unlinked_b2.discard(n2)
            
      print unlinked_f1, unlinked_f2
      
      unlinked_b1 = list(unlinked_b1)
      random.shuffle(unlinked_b1)
      for i in sorted(list(unlinked_f1)):
        nxt1[i] = unlinked_b1.pop()
        while test_loop(nxt1, i):
          print unlinked_b1
          unlinked_b1.insert(nxt1[i], 0)
          nxt1[i] = unlinked_b1.pop()
          
      unlinked_b2 = list(unlinked_b2)
      random.shuffle(unlinked_b2)
      for i in sorted(list(unlinked_f2)):
        nxt2[i] = unlinked_b2.pop()
        while test_loop(nxt2, i):
          print unlinked_b2
          unlinked_b2.insert(nxt2[i], 0)
          nxt2[i] = unlinked_b2.pop()
        
      if mut:
        r1 = random.randrange(0,len(towns))
        r2 = random.randrange(0,len(towns))
        temp = nxt1[r1]
        nxt1[r1] = nxt1[r2]
        nxt1[r1] = temp
        temp = nxt2[r1]
        nxt2[r1] = nxt2[r2]
        nxt2[r1] = temp
        
      for i in xrange(len(towns)):
        print "%2d %2d %2d" %(i, nxt1[i], nxt2[i])
      print "------"

      
      return [cls(nxt1), cls(nxt2)]

  genetic( Travelling_Salesman, 4, 50, .3, .2 )



