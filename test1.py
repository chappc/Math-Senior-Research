#! /usr/bin/env python
import pygame
import OpenGL
OpenGL.USE_ACCELERATOR = True
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

vertices= (
  (1, -1, -1),
  (1, 1, -1),
  (-1, 1, -1),
  (-1, -1, -1),
  (1, -1, 1),
  (1, 1, 1),
  (-1, -1, 1),
  (-1, 1, 1)
  )

edges = (
  (0,1),
  (0,3),
  (0,4),
  (2,1),
  (2,3),
  (2,7),
  (6,3),
  (6,4),
  (6,7),
  (5,1),
  (5,4),
  (5,7)
  )

radius = .1

def cube( q ):
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


def main():
  # Start pygame
  pygame.init()
  display = (1024,720)
  pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

  # Set background color
  glClearColor (.8, .8, .8, 1.0)
  # Set object color
  glColor3fv((.3, .5, .7))
  #
  glEnable(GL_COLOR_MATERIAL)

  # Set shader properties of objects
  glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.7, 0.7, 0.7, 1.0))
  glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
  glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, (50.0))
  glShadeModel (GL_SMOOTH);

  # Set light position and intensity
  glLightfv( GL_LIGHT0, GL_POSITION, ( -20, 100, -0.5, 0.1 ) )

  # Allow GL to figure out how to render objects with depth
  glEnable(GL_DEPTH_TEST)
  glEnable(GL_AUTO_NORMAL)
  #glEnable(GL_NORMALIZE)

  quadric=gluNewQuadric()
  gluQuadricNormals(quadric, GLU_SMOOTH)
  gluQuadricTexture(quadric, GL_TRUE)

  gluPerspective(40, (1.0*display[0]/display[1]), 0.1, 50.0)
  glTranslatef(0.0, 0.0, -10)
  glEnable(GL_DEPTH_TEST)
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glRotatef(2, 0, 0, 0)
    cube(quadric)
    glDisable(GL_LIGHTING)
    pygame.display.flip()
    pygame.time.wait(10)

if __name__=="__main__":
  main()

