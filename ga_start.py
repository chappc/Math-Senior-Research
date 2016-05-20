import random
from copy import deepcopy
from deap import base, creator, tools
import Image, ImageChops, ImageDraw
import math, operator
import threading

from test_shadow import cast_shadow_sphere
import renderObject

NUM_NODES = 30
RADIUS = 0.0125
#LIGHTS = [(0.0,1.0,1.0),(0.01,1.0,1.0),(-0.01,1.0,1.0),(0.0,0.01,1.0),(0.0,-0.01,1.0),(0.007071,0.007071,1.0),(-0.007071,0.007071,1.0),(0.007071,-0.007071,1.0),(-0.007071,-0.007071,1.0)]
LIGHTS = [(0.0,1.0,1.0)]
PROJECTION = (0.00625, 0.99375, 1.0)
REGION = (0.0, 1.0, 0.0, 1.0)
N_IND = 200
N_GEN = 500
CR_PROB = .6
MUT_PROB = 0.12

original_canvas = None

blank_canvas = None
canvases = None
final_canvas = None
mask = None
dif = None
difmask = None
im = None
edges = []
vertices = []
threadLock = threading.Lock()

def diff(im1, im2):
    "Calculate the root-mean-square difference between two images"

    h = ImageChops.difference(im1, im2).load()
    sum = 0
    for i in xrange(im1.width):
      for j in xrange(im1.height):
        sum += (h[i,j]/255.0)**2
    return sum/(i*j)


def resetCanvas():
  for canvas in canvases:
    canvas.paste(blank_canvas)
  return [canvas.load() for canvas in canvases]

def calculate_loc(x, y, z):
  lightx, lighty, lightz = PROJECTION
  y = (y+1) % 1
  x = (x+1) % 1
  z = pow((z+1) % 1, 1.5)
  z_skew = (lightz - z)/lightz
  y_skew = lighty + (y - lighty)*z_skew
  x_skew = lightx + (x - lightx)*z_skew
  return (x_skew, y_skew, z)

def evaluate(individual):
  pix = resetCanvas()
  final_canvas.paste(blank_canvas)
  for p, l in zip(pix,LIGHTS):
    for i in xrange(0,len(individual),3):
      loc = calculate_loc(individual[i],individual[i+1],individual[i+2])
      cast_shadow_sphere(p, l, loc, RADIUS, REGION, RESOLUTION)
  for c in canvases:
    final_canvas.paste(c,(0,0),mask)
  
  dif.paste(final_canvas)
  dif.paste(original_canvas.convert('RGBA'), (0,0), difmask)
  # find the largest z position
  zmax = max([((.6-individual[x])*2)**2 for x in xrange(2,len(individual),3)])
  return diff(final_canvas.convert('L'), original_canvas.convert('L')), zmax*0.3

def set_view(individual):
  threadLock.acquire()
  del vertices[:]
  for i in xrange(0,len(individual),3):
    vertices.append(calculate_loc(individual[i],individual[i+1],individual[i+2]))
  im.paste(dif)
  threadLock.release()

def make_poster(ind, res, r):
  c = Image.new('RGBA', res, "white")
  cd = ImageDraw.Draw(c)
  rad = int(res[0]*r)
  thk = res[0]/1000 + 1
  for i in xrange(0,len(ind),3):
    x,y,z = calculate_loc(ind[i],ind[i+1],ind[i+2])
    xpix = int(x*res[0])
    ypix = int((PROJECTION[2]-y)*res[0])
    zpix = int(z*res[1])
    zoff = zpix + ypix
    color = "#%06x"%(random.randint(0, 0xffffff))
    cd.ellipse([xpix-rad, zoff-rad, xpix+rad, zoff+rad], outline=color, fill=color)
    cd.line([(xpix,zpix),(xpix,zoff)], fill=color, width=thk)
  for l in LIGHTS:
    xpix = int(l[0]*res[0])
    ypix = int(l[1]*res[1])
    zpix = int(l[2]*res[1])
    color = "yellow"
    cd.ellipse([xpix-10, zoff-10, xpix+10, zoff+10], outline=color)
  return c

class render (threading.Thread):
  def __init__(self, threadID, name, counter):
    threading.Thread.__init__(self)
    self.threadID = threadID
    self.name = name
    self.counter = counter

  def run(self):
    q = renderObject.setup_GL()
    while True:
      renderObject.get_key_input()
      threadLock.acquire()
      strdata = im.transpose(1).tostring()
      threadLock.release()
      renderObject.draw_scheme(REGION, q, edges, vertices, PROJECTION, RADIUS, strdata, RESOLUTION)

def attr():
  x = random.gauss(0.5, 0.2)
  while x <= 0 or x >= 1:
    x = random.gauss(0.5, 0.2)
  return x


class GA():
  def __init__(self):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0))
    creator.create("NodeList", list, radius=RADIUS, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("attribute", attr)
    toolbox.register("individual", tools.initRepeat, creator.NodeList,
                    toolbox.attribute, n=NUM_NODES*3)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mate", tools.cxBlend, alpha=.6)
    toolbox.register("mutate", tools.mutGaussian, mu=0.0, sigma=2.*RADIUS, indpb=math.sqrt(1.0/NUM_NODES))
    #toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate)
    self.toolbox = toolbox
    self.winner = None

  def rand_pop(self, n_ind):
    self.pop = [self.toolbox.individual() for i in xrange(n_ind)]
    return self.pop
  
  def run(self, n_gen, pop=[]):
    if pop==[]:
      pop = self.pop

    
    for ind in pop:
      ind_unsorted = ind
      bins = {}
      granularity = math.sqrt(NUM_NODES)
      for i in xrange(0,len(ind),3):
        b = (int(ind[i]*granularity)+int(ind[+1]*granularity))*((ind[i]*granularity)-int(ind[+1]*granularity))**2
        if b in bins:
          bins[b].append(i)
        else:
          bins[b] = [i]
      count = 0
      for b in sorted(bins.keys()):
        for i in bins[b]:
          ind[count] = ind_unsorted[i]
          ind[count+1] = ind_unsorted[i+1]
          ind[count+2] = ind_unsorted[i+2]
          count += 1
      ind.fitness.values = self.toolbox.evaluate(ind)
      #print ind.fitness.values
      set_view(ind)

    winner = pop[0]
    for ind in pop[1:]:
      if ind.fitness.values[0] < winner.fitness.values[0]:
        winner = ind
    count = 0

    for g in xrange(n_gen):
      print "Generation", g
      count += 1
      # Select the next generation individuals
      offspring = self.toolbox.select(pop, len(pop))
      # Clone the selected individuals
      offspring = map(self.toolbox.clone, offspring)

      # Apply crossover on the offspring
      for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CR_PROB:
          self.toolbox.mate(child1, child2)
          del child1.fitness.values
          del child2.fitness.values

      # Apply mutation on the offspring
      for mutant in offspring:
        if random.random() < MUT_PROB:
          self.toolbox.mutate(mutant)
          del mutant.fitness.values

      # Evaluate the individuals with an invalid fitness
      invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
      for ind in invalid_ind:
        ind.fitness.values = self.toolbox.evaluate(ind)
        if ind.fitness.values[0] < winner.fitness.values[0]:
          winner = ind
          count = 0
        #print ind.fitness.values
        set_view(ind)

      # The population is entirely replaced by the offspring
      pop[:] = offspring
    
      # ten generations with no improvement
      if count >= n_gen/20:
        break
        
    print "\n\nWinner!\n", winner, "\nwith fitness ", evaluate(winner)
    dif.paste(final_canvas)
    set_view(winner)
    if self.winner == None or self.winner.fitness.values[0] > winner.fitness.values[0]:
      self.winner = deepcopy(winner)
      make_poster( self.winner, (9000, 9000), RADIUS ).save("poster_chair_"+g+".png", "PNG")
    return winner
  
  def run_multiple(self, pop_size, n_gen, n_sectors):
    win_pop = []
    for x in xrange(n_sectors):
      print "Run", x
      self.rand_pop(pop_size)
      win_pop.append(self.run(n_gen))
    self.run(n_gen, win_pop)
    return self.winner
  
  
  
if __name__=="__main__":
  
  if len(sys.argv) < 4:
    print 'usage: python ', sys.argv[0], '<input_shadow> <sphere-radius> <n_spheres>'
    sys.exit(1)
    
  NUM_NODES = sys.argv[3]
  RADIUS = sys.argv[2]
    
  original_canvas = Image.open(sys.argv[1], 'r')
  RESOLUTION = original_canvas.size
  
  blank_canvas = Image.new('L', RESOLUTION, "white")
  canvases = [Image.new('L', RESOLUTION, "white") for x in LIGHTS]
  final_canvas = Image.new('RGBA', RESOLUTION, "white")
  mask = Image.new('RGBA', RESOLUTION, (255,255,255,255/len(LIGHTS)))
  dif = Image.new('RGBA', RESOLUTION, "white")
  difmask = Image.new('RGBA', RESOLUTION, (0,0,255,64))
  im = Image.new('RGBA', RESOLUTION, "white")

  
  thd = render(1, 'render_thread', 1)
  thd.start()

  g = GA()
  w = g.run_multiple(N_GEN, N_IND, 20)
  set_view(w)
  
  final_canvas.save("output_chair.png","PNG")
  make_poster( w, (9000, 9000), RADIUS ).save("poster_chair.png", "PNG")

# An example set of nodes
"""
[0.669316359495516, 0.8786361884175978, -0.12914515448134428, 1.3737237178654997, -0.4179486508622152, 0.054630455931436644, -0.13115131528269786, 0.506677420551265, 0.1052087338193465, 0.2091780582747533, 0.36837344953433626, 0.2742494660364548, 0.49149119940878844, 0.853800542816882, 0.358683597516535, 0.42606856108020613, 4.549647031551695, 0.3684101176017201, 0.4315628261742692, 0.3992349908803633, 0.3792743667959751, 0.7750731778053679, 0.3459859121103988, 0.38733671066585684, 0.4958459960839606, 0.654314300888096, 0.40234286371213973, -3.5679184417609227, 0.32576407619396347, 0.41696039470678925, 0.4848959088242933, 0.6680788018301153, 0.5572948931250068, 0.3960049974743814, 0.5972085665764231, 0.6009857287193738, 0.5728270862951581, 0.41850512150256736, 0.6232006441396265, 0.8923143830807874, 0.1598359744444511, 0.6633349763626302, 0.2802868566221288, 0.3503061790049036, 0.6927135182594379, 0.4371031361889797, 0.3826306218336196, 0.7556747987015366, 0.5197720000950157, 0.23167293027298888, 0.760309541667037, 0.4369235666694813, 0.7378469142417843, 0.8350709384854299, 0.2201473025911713, 0.2935133711468777, 0.8420280547318663, 0.4810060901547438, 0.8172721412850502, 0.8476623271112064, 0.7548978700256253, 0.6634578372029551, 0.8490330244051729, 0.36091219444616274, 0.5693817738112044, 0.8527548461578318, 0.4817939348352729, 0.19086253941864356, 0.8551168232750943, 0.40855093596170056, 0.6309515230367053, 0.8706961999300601, 0.5484494099243666, 0.8916950508349166, 0.8714847193548565, 0.7856991847104724, 0.8195460583425671, 0.8859995515275587, 0.46581560751569673, 0.38450960220041563, 0.8951201055246604, 0.6430025229689946, 0.41839897597684617, 0.9065590704987587, 0.25691080140140626, 0.49251568558142256, 0.9236924201381929, 0.7145218000713363, 0.5434241722527415, 1.8561974289065342]
"""