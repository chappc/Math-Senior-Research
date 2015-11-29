#! /usr/bin/env python
import pygame
import OpenGL
OpenGL.USE_ACCELERATOR = True
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys
from ADParser import parse_file

def loadImage(filename):
  textureSurface = pygame.image.load(filename)
  textureData = pygame.image.tostring(textureSurface, "RGBA", 1)

  width = textureSurface.get_width()
  height = textureSurface.get_height()

  return textureData, width, height

def bindImage( textureData, width, height ):
  texture = glGenTextures(1)
  glBindTexture(GL_TEXTURE_2D, texture)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
  glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, \
    GL_UNSIGNED_BYTE, textureData)
  return texture

def createTexDL(width, height, vertices):
  newList = glGenLists(1)
  glNewList(newList,GL_COMPILE);
  glBegin(GL_QUADS)
  vertex = vertices[0]

  # Bottom Left Of The Texture and Quad
  glTexCoord2f(0, 0)
  glVertex2f(vertex[0], vertex[1])

  vertex = vertices[1]
  # Bottom Right Of The Texture and Quad
  glTexCoord2f(1, 0)
  glVertex2f(vertex[0], vertex[1])

  vertex = vertices[2]
  # Top Right Of The Texture and Quad
  glTexCoord2f(1, 1)
  glVertex2f(vertex[0], vertex[1])

  vertex = vertices[3]
  # Top Left Of The Texture and Quad
  glTexCoord2f(0, 1)
  glVertex2f(vertex[0], vertex[1])

  glEnd()
  glEndList()

  return newList

def cube( q, edges, vertices, radius ):
  for edge in edges:
    cylinder( q, vertices[edge[0]], vertices[edge[1]], radius )
  for vertex in vertices:
    sphere( q, vertex, radius )


def sphere( q, v, r ):
  x,y,z = v

  glPushMatrix()
  glTranslatef( x, y, z )
  gluSphere( q, r, 20, 20 )
  glPopMatrix()

def cylinder( q, v1, v2, r ):
  x1, y1, z1 = v1
  x2, y2, z2 = v2
  if ( x2 <= x1 and \
       y2 <= y1 and \
       z2 <= z1 ):
    x1, y1, z1 = v2
    x2, y2, z2 = v1
  vx = float(x2-x1)
  vy = float(y2-y1)
  vz = float(z2-z1)

  #handle the degenerate case of z1 == z2 with an approximation
  if vz == 0:
    vz = .000001

  v = math.sqrt( vx*vx + vy*vy + vz*vz )
  ax = 57.2957795*math.acos( vz/v )
  if vz < 0.0:
    ax = -ax
  rx = -vy*vz
  ry = vx*vz

  glPushMatrix()

  #draw the cylinder body
  glTranslatef( x1, y1, z1 )
  glRotatef( ax, rx, ry, 0.0 )
  gluCylinder( q, r, r, v, 20, 1 )
  glPopMatrix()

def build_v_and_e(strands):
  verticies = []
  edges = []
  i = 0
  for strand in strands:
    verticies.append(strand[0])
    i += 1
    for p in strand[1:]:
      verticies.append(p)
      edges.append((i-1,i))
      i += 1
  return verticies,edges
  
def main(strandFile, shadowFile):
  lights, radius, region, resolution, strands = parse_file(strandFile)
  vertices,edges = build_v_and_e(strands)
  
  x0,x1,y0,y1 = region
  verticesW = (
    (x0, y0, 0),
    (x1, y0, 0),
    (x1, y1, 0),
    (x0, y1, 0)
    )
  
  edgesW = (
    (0,1),
    (1,2),
    (2,3),
    (0,3)
    )
  
  # Start pygame
  pygame.init()
  display = (1024,720)
  pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

  # Set background color
  glClearColor (.8, .8, .8, 1.0)
  #
  glEnable(GL_COLOR_MATERIAL)
  glEnable(GL_TEXTURE_2D)

  # Set shader properties of objects
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (0.7, 0.7, 0.7, 1.0))
  glMaterialfv(GL_FRONT, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
  glMaterialfv(GL_FRONT, GL_SHININESS, (100.0))
  glShadeModel (GL_SMOOTH);

  # Set light position and intensity
  glLightfv( GL_LIGHT0, GL_POSITION, ( -20, 100, -0.5, 0.2 ) )
  glLightfv( GL_LIGHT0, GL_DIFFUSE, ( 1, 1, 1, .2 ) )
  glLightfv( GL_LIGHT0, GL_SPECULAR, ( 1, 1, 1, .2 ) )
  glLightfv( GL_LIGHT0, GL_AMBIENT, ( .8, .8, .8, 1 ) )

  # Allow GL to figure out how to render objects with depth
  glEnable(GL_DEPTH_TEST)
  glEnable(GL_AUTO_NORMAL)
  #glEnable(GL_NORMALIZE)

  quadric=gluNewQuadric()
  gluQuadricNormals(quadric, GLU_SMOOTH)
  gluQuadricTexture(quadric, GL_TRUE)

  # get texture from filename
  texData, width, height = loadImage(shadowFile)

  gluPerspective(20, (1.0*display[0]/display[1]), 0.1, 50.0)
  glTranslatef(0.0, 0.0, -10)
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glRotatef(2, 1, 5, 3)
    # Set object color
    glColor3fv((.1, .2, .3))
    cube(quadric, edges, vertices, radius)
    cube(quadric, edgesW, verticesW, 0.02)
    glPushMatrix()
    glTranslatef(0,0,verticesW[0][2])
    # Set object color
    glColor3fv((1, 1, 1))
    texture = bindImage(texData, width, height)
    glBindTexture(GL_TEXTURE_2D, texture)
    glCallList(createTexDL(width, height, verticesW))
    glPopMatrix()
    glDeleteTextures([texture])
    glDisable(GL_LIGHTING)
    pygame.display.flip()
    pygame.time.wait(10)

if __name__=="__main__":
    if len(sys.argv) < 3:
        print 'usage: python ', sys.argv[0], '<strand-file> <shadow-file>'
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
