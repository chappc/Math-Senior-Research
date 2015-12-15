import pygame
import numpy as np
from OpenGL.GL import *
 
##########################################
# Define the simple pass-through shaders
##########################################
import cStringIO
vshade = cStringIO.StringIO("""
#version 110
 
uniform mat4 p_matrix;
uniform mat4 mv_matrix;
 
attribute vec4 position;
 
void main()
{
   vec4 eye_position = mv_matrix * position;
   gl_Position = p_matrix * eye_position;
}
""")
 
fshade = cStringIO.StringIO("""
#version 110
 
void main()
{
   gl_FragColor = vec4(1.0,0.0,0.0,1.0);
}
""")
 
###################################################
# Set up a simple square composed of two triangles
###################################################
verts = np.array([[0,0,0,1],[1,0,0,1],[1,1,0,1],[0,1,0,1]]).astype(np.float32)
polys = np.array([[0,1,3],[1,2,3]]).astype(np.ushort)
mv_matrix = np.eye(4)
mv_matrix[:3,-1] = [0,0,2]
projection = np.array([ [ 1.071429,  0.      ,  0.      ,  0.      ],
                       [ 0.      ,  1.428571,  0.      ,  0.      ],
                       [ 0.      ,  0.      ,  1.000489, -0.125031],
                       [ 0.      ,  0.      ,  1.      ,  0.      ]])
 
def _make_shader(stype, src):
    shader = glCreateShader(stype)
    glShaderSource(shader, src)
    glCompileShader(shader)
 
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        err = glGetShaderInfoLog(shader)
        glDeleteShader(shader)
        raise Exception(err)
    return shader
 
##################################
# Initialize pygame and opengl
##################################
flags = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.OPENGL
pygame.display.set_mode((800,600), flags)
 
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glClearColor(0.5,0.5,0.5,1)
glClearDepth(1.0)
glDepthFunc(GL_LESS)
glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)
 
 
######################################
# Make the shaders and programs
######################################
vshade = _make_shader(GL_VERTEX_SHADER, vshade.read())
fshade = _make_shader(GL_FRAGMENT_SHADER, fshade.read())
 
program = glCreateProgram()
glAttachShader(program, vshade)
glAttachShader(program, fshade)
glLinkProgram(program)
 
#######################################
# Fetch positions, push poly to card
#######################################
posidx = glGetAttribLocation(program, "position")
pidx = glGetUniformLocation(program, "p_matrix")
mvidx = glGetUniformLocation(program, "mv_matrix")
 
vbuf = glGenBuffers(1)
ebuf = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbuf)
glBufferData(GL_ARRAY_BUFFER,
    verts.astype(np.float32).ravel(), GL_STATIC_DRAW)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebuf)
glBufferData(GL_ELEMENT_ARRAY_BUFFER,
    polys.astype(np.uint16).ravel(), GL_STATIC_DRAW)
 
#####################################
# Enter main drawing loop!
#####################################
glViewport(0,0,800,600)
while True:
    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glUseProgram(program)
 
    # Push the transforms to the card
    glUniformMatrix4fv(pidx, 1, GL_TRUE, projection.astype(np.float32))
    glUniformMatrix4fv(mvidx, 1, GL_TRUE, mv_matrix.astype(np.float32))
 
    # Enable the position attribute
    glEnableVertexAttribArray(posidx)
    glBindBuffer(GL_ARRAY_BUFFER, vbuf)
    glVertexAttribPointer( posidx, 4, GL_FLOAT, GL_FALSE, 4*4, 0)
 
    # Draw the two triangles
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebuf);
    glDrawElements(
        GL_TRIANGLES,           # mode
        len(polys)*3,           # count
        GL_UNSIGNED_SHORT,      # type
        0                       # element array buffer offset
    )
    glDisableVertexAttribArray(posidx)
 
    #inspect the values -- does it make sense?
    glBindBuffer(GL_ARRAY_BUFFER, vbuf)
    l, l2 = (GLfloat*16)() , (GLushort*6)()
    glGetBufferSubData(GL_ARRAY_BUFFER, 0, 4*4*4, l)
    print list(l)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebuf)
    glGetBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, 2*6, l2)
    print list(l2)
    glGetUniformfv(program, pidx, l)
    print list(l)
    glGetUniformfv(program, mvidx, l)
    print list(l)
 
    pygame.display.flip()