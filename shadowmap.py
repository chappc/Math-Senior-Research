#! /usr/bin/env python

# This program was *heavily* based on tutorial16_SimpleVersion.cpp found at
# https://github.com/opengl-tutorials/ogl/blob/master/tutorial16_shadowmaps/tutorial16_SimpleVersion.cpp

import pygame
import OpenGL
OpenGL.USE_ACCELERATOR = True
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import sys
from ctypes import *
from test1 import loadImage, bindImage
import numpy as np
import Image

import cStringIO
from shadowmappingshaders import *

def _make_shader(stype, src):
    shader = glCreateShader(stype)
    glShaderSource(shader, src)
    glCompileShader(shader)
 
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        err = glGetShaderInfoLog(shader)
        glDeleteShader(shader)
        raise Exception(err)
    return shader

def LoadShaders(vshade,fshade):
    vshadeID = _make_shader(GL_VERTEX_SHADER, vshade.read())
    fshadeID = _make_shader(GL_FRAGMENT_SHADER, fshade.read())
     
    ProgramID = glCreateProgram()
    glAttachShader(ProgramID, vshadeID)
    glAttachShader(ProgramID, fshadeID)
    glLinkProgram(ProgramID)
    return ProgramID

pygame.init()
display = (1024,768)
pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

glClearColor(0.0, 0.0, 0.4, 0.0)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
glEnable(GL_CULL_FACE)

VertexArrayID = glGenVertexArrays(1)
glBindVertexArray(VertexArrayID)

depthProgramID = LoadShaders(vshadeDRTT,fshadeDRTT)

depthMatrixID = glGetUniformLocation(depthProgramID, "depthMVP")

texData, width, height = loadImage('art-description-shadow.jpeg')
Texture = bindImage(texData, width, height)

indices = np.array([0,1,3,1,2,3]).astype(np.ushort)
indexed_vertices = \
        np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],\
                  [0,1,-1],[1,1,-1],[1,0,-1],[0,0,-1]]).astype(np.float32)
indexed_uvs = np.array([[0,0],[1,0],[1,1],[0,1],\
                        [0,0],[1,0],[1,1],[0,1]]).astype(np.float32)
indexed_normals = np.array([[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1],\
                            [-1,1,-1],[1,1,-1],[1,-1,-1],[-1,-1,-1]]).astype(np.float32)

vertexbuffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
glBufferData(GL_ARRAY_BUFFER, indexed_vertices, GL_STATIC_DRAW)

uvbuffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
glBufferData(GL_ARRAY_BUFFER, indexed_uvs, GL_STATIC_DRAW)

normalbuffer = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, normalbuffer)
glBufferData(GL_ARRAY_BUFFER, indexed_normals, GL_STATIC_DRAW)

elementbuffer = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, elementbuffer)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

FramebufferName = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, FramebufferName)

im = Image.new('F',(1024,1024),'white')
image = im.tostring("raw", "F", 0, -1) # What do the last two parameters do?

depthTexture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, depthTexture)
glTexImage2D(GL_TEXTURE_2D, 0,GL_DEPTH_COMPONENT16, 1024, 1024, 0,GL_DEPTH_COMPONENT, GL_FLOAT, image)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE, GL_COMPARE_R_TO_TEXTURE)

glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, depthTexture, 0)

glDrawBuffer(GL_NONE)

if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
    quit()

programID = LoadShaders(vshadeSM_simple, fshadeSM_simple)

TextureID = glGetUniformLocation(programID, "myTextureSampler")

MatrixID = glGetUniformLocation(programID, "MVP")
DepthBiasID = glGetUniformLocation(programID, "DepthBiasMVP")
ShadowMapID = glGetUniformLocation(programID, "shadowMap")

def quit_routine():
    glDeleteBuffers(1, [vertexbuffer]);
    glDeleteBuffers(1, [uvbuffer]);
    glDeleteBuffers(1, [normalbuffer]);
    glDeleteBuffers(1, [elementbuffer]);
    glDeleteProgram(programID);
    glDeleteProgram(depthProgramID);
    glDeleteTextures(1, [Texture]);

    glDeleteFramebuffers(1, [FramebufferName]);
    glDeleteTextures(1, [depthTexture])

    pygame.quit()
    quit()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_routine()
    
    glBindFramebuffer(GL_FRAMEBUFFER, FramebufferName)
    glViewport(0,0,1024,1024)
    
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glUseProgram(depthProgramID)
    
    # glm::vec3 lightPos(5, 20, 20);
    # glm::mat4 depthProjectionMatrix = glm::perspective<float>(45.0f, 1.0f, 2.0f, 50.0f);
    # glm::mat4 depthViewMatrix = glm::lookAt(lightPos, lightPos-lightInvDir, glm::vec3(0,1,0));
    
    depthMVP = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]).astype(np.float32)
    
    glUniformMatrix4fv(depthMatrixID, 1, GL_FALSE, depthMVP)
    
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
    glVertexAttribPointer(\
			0,  #// The attribute we want to configure\
			3,                  #// size\
			GL_FLOAT,           #// type\
			GL_FALSE,           #// normalized?\
			0,                  #// stride\
			0                   #// array buffer offset\
		)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, elementbuffer)
    
    glDrawElements(\
			GL_TRIANGLES,      #// mode\
			len(indices),      #// count\
			GL_UNSIGNED_SHORT, #// type\
			indices            #c++ comment appears to be wrong: applied to an arg of 0, which failed: // element array buffer offset\
		)
        
    glDisableVertexAttribArray(0)
    
    # // Render to the screen
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glViewport(0,0,display[0],display[1])
    
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glUseProgram(programID)
    
    # matrix computations go here
    # ...
    
    MVP = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]).astype(np.float32)
    depthBiasMVP = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]).astype(np.float32)
    
    glUniformMatrix4fv(MatrixID, 1, GL_FALSE, MVP);
    glUniformMatrix4fv(DepthBiasID, 1, GL_FALSE, depthBiasMVP)
    
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, Texture)
    glUniform1i(TextureID, 0)
    
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, depthTexture)
    glUniform1i(ShadowMapID, 1)
    
    glEnableVertexAttribArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer)
    glVertexAttribPointer(\
			0,                  #// attribute\
			3,                  #// size\
			GL_FLOAT,           #// type\
			GL_FALSE,           #// normalized?\
			0,                  #// stride\
			0                   #// array buffer offset\
		)
        
    glEnableVertexAttribArray(1)
    glBindBuffer(GL_ARRAY_BUFFER, uvbuffer)
    glVertexAttribPointer(\
			1,                                #// attribute\
			2,                                #// size\
			GL_FLOAT,                         #// type\
			GL_FALSE,                         #// normalized?\
			0,                                #// stride\
			0                          #// array buffer offset\
		)
    
    glEnableVertexAttribArray(2)
    glBindBuffer(GL_ARRAY_BUFFER, normalbuffer)
    glVertexAttribPointer(\
			2,                                #// attribute\
			3,                                #// size\
			GL_FLOAT,                         #// type\
			GL_FALSE,                         #// normalized?\
			0,                                #// stride\
			0                          #// array buffer offset\
		)
    
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, elementbuffer)
    
    glDrawElements(\
			GL_TRIANGLES,      #// mode\
			len(indices),      #// count\
			GL_UNSIGNED_SHORT, #// type\
			indices           # again, this seems to be wrong: // element array buffer offset\
		)
    
    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)
    glDisableVertexAttribArray(2)
    
    pygame.display.flip()
    pygame.time.wait(10)
    