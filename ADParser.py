

error_msg = 'This file is not a valid art description. See "ad file spec.txt"'
ADParseError = RuntimeError(error_msg)

def parse_lights(file):
  line = file.readline()
  if not line == 'lights section:\n':
    raise ADParseError
  
  lights = []
  line = file.readline()
  while not (line == '\n' or line == ''):
    lights.append( [float(x) for x in line.split(',')] )
    line = file.readline()
  if not lights: # If lights is empty
    raise ADParseError
  return lights
        
def parse_radius(file):
  line = file.readline()
  parts = line.split('=')
  if len(parts) != 2 or parts[0] != 'radius':
    raise ADParseError
  return float(parts[1])
  
def parse_region(file):
  line = file.readline()
  parts = line.split('=')
  if len(parts) != 2 or parts[0] != 'region':
    raise ADParseError
  region = [float(x) for x in parts[1].split(',')]
  if len(region) != 4:
    raise ADParseError
  return region
  
def parse_resolution(file):
  line = file.readline()
  parts = line.split('=')
  if len(parts) != 2 or parts[0] != 'resolution':
    raise ADParseError
  resolution = [int(x) for x in parts[1].split(',')]
  if len(resolution) != 2:
    raise ADParseError
  return resolution

def parse_strands(file):
  line = file.readline()
  if not line == 'strands section:\n':
    raise ADParseError
  
  strands = []
  while True:
    line = file.readline()
    if line == '\n' or line == '':
      break
    strands.append([])
    while not (line == '\n' or line == ''):
      strands[-1].append( [float(x) for x in line.split(',')] )
      line = file.readline()
  return strands

def parse_file(infile):
  f = open(infile,'r')
  lights = parse_lights(f)
  radius = parse_radius(f)
  region = parse_region(f)
  resolution = parse_resolution(f)
  line = f.readline()
  if not line == '\n':
    raise ADParseError
  strands = parse_strands(f)
  f.close()
  return lights, radius, region, resolution, strands
  