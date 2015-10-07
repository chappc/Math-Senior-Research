import OpenGL
#OpenGL.FULL_LOGGING = True
from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGLContext.scenegraph.basenodes import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.depth_texture import *
from OpenGL.GL.ARB.shadow import *
from OpenGLContext.arrays import (
    array, sin, cos, pi, dot, transpose,
)
from OpenGLContext.events.timer import Timer

from OpenGLContext.passes import flatcompat as flat
class TestContext( BaseContext ):
  """Shadow rendering tutorial code"""

  initialPosition = (.5,1,3)
  lightViewDebug = False

  def OnInit( self ):
    """Initialize the context with GL active"""
    if not glInitShadowARB() or not glInitDepthTextureARB():
      print 'Missing required extensions!'
      sys.exit( testingcontext.REQUIRED_EXTENSION_MISSING )

    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glEnable( GL_POLYGON_SMOOTH )
    self.geometry = self.createGeometry()
    self.geometryPasses = flat.FlatPass(self.geometry,self)
    self.time = Timer( duration = 8.0, repeating = 1 )
    #self.time.addEventHandler( "fraction", self.OnTimerFraction )
    self.time.register (self)
    self.time.start ()
    self.lights = self.createLights()
    self.addEventHandler( "keypress", name="s", function = self.OnToggleTimer)

  def createLights( self ):
    """Create the light's we're going to use to cast shadows"""
    return [
            SpotLight(
              location = [0,5,10],
              color = [1,.95,.95],
              intensity = 1,
              ambientIntensity = 0.10,
              direction = [0,-5,-10],
            ),
            SpotLight(
              location = [3,3,3],
              color = [.75,.75,1.0],
              intensity = .5,
              ambientIntensity = .05,
              direction = [-3,-3,-3],
            ),
        ]
  def createGeometry( self ):
    """Create a simple VRML scenegraph to be rendered with shadows"""
    return Transform(
      children = [
        Transform(
          translation = (0,-.38,0),
          children = [
            Shape(
              DEF = 'Floor',
              geometry = Box( size=(5,.05,5)),
              appearance = Appearance( material=Material(
                diffuseColor = (.7,.7,.7),
                shininess = .8,
                ambientIntensity = .1,
              )),
            ),
          ],
        ),
        Transform(
          translation = (0,0,0),
          children = [
            Shape(
              DEF = 'Tea',
              geometry = Teapot( size = .5 ),
              appearance = Appearance(
                material = Material(
                  diffuseColor =( .5,1.0,.5 ),
                  ambientIntensity = .2,
                  shininess = .5,
                ),
              ),
            )
          ],
        ),
        #Transform(
          #translation = (2,3.62,0),
          #children = [
            #Shape(
              #DEF = 'Pole',
              #geometry = Box( size=(.1,8,.1) ),
              #appearance = Appearance(
                #material = Material(
                  #diffuseColor =( 1.0,0,0 ),
                  #ambientIntensity = .4,
                  #shininess = 0.0,
                #),
              #),
            #)
          #],
        #),
      ],
    )

  def OnTimerFraction( self, event ):
    """Update light position/direction"""
    light = self.lights[0]
    a = event.fraction() * 2 * pi
    xz = array( [
      sin(a),cos(a),
    ],'f') * 10 # radius
    position = light.location
    position[0] = xz[0]
    position[2] = xz[1]
    light.location = position
    light.direction = -position

  def OnToggleTimer( self, event ):
    """Allow the user to pause/restart the timer."""
    if self.time.active:
      self.time.pause()
    else:
      self.time.resume()

  def Render( self, mode):
    assert mode
    BaseContext.Render( self, mode )
    self.geometryPasses.setViewPlatform( mode.viewPlatform )
    if mode.visible and mode.lighting and not mode.transparent:
      shadowTokens = [
        (light,self.renderLightTexture( light, mode ))
        for light in self.lights[:self.lightViewDebug or len(self.lights)]
      ]
      glClear(GL_DEPTH_BUFFER_BIT)
      platform = self.getViewPlatform()
      platform.render( identity = True )
      self.renderAmbient( mode )
      glEnable(GL_BLEND)
      glBlendFunc(GL_ONE,GL_ONE)
      try:
        for i,(light,(texture,textureMatrix)) in enumerate(shadowTokens):
          self.renderDiffuse( light, texture, textureMatrix, mode, id=i )
      finally:
        glDisable(GL_BLEND)
    else:
      self.drawScene( mode, mode.getModelView() )

  def drawScene( self, mode, matrix ):
    """Draw our scene at current animation point"""
    glMatrixMode( GL_MODELVIEW )
    glLoadMatrixf( matrix )
    glPushMatrix()
    try:
      self.geometryPasses.renderGeometry( matrix )
    finally:
      glPopMatrix()

  offset = 1.0

  def renderLightTexture( self, light, mode,direction=None, fov = None, textureKey = None ):
    """Render ourselves into a texture for the given light"""
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_DEPTH_TEST)
    glPushAttrib(GL_VIEWPORT_BIT)
    texture = self.setupShadowContext(light,mode)
    if fov:
      cutoff = fov /2.0
    else:
      cutoff = None
    lightView = light.viewMatrix(
      cutoff, near=.3, far=30.0
    )
    lightModel = light.modelMatrix( direction=direction )
    lightMatrix = dot( lightModel, lightView )
    textureMatrix = transpose(
      dot(
        lightMatrix,
        self.BIAS_MATRIX
      )
    )
    glMatrixMode( GL_PROJECTION )
    glLoadMatrixf( lightView )
    glMatrixMode( GL_MODELVIEW )
    glLoadMatrixf( lightModel )
    self.geometryPasses.matrix = lightModel
    self.geometryPasses.modelView = lightModel
    self.geometryPasses.projection = lightView
    self.geometryPasses.viewport = mode.viewport
    self.geometryPasses.calculateFrustum()
    self.geometryPasses.context = self
    self.geometryPasses.cache = mode.cache
    try:
      if not self.lightViewDebug:
        glColorMask( 0,0,0,0 )
      self.geometryPasses.lighting = False
      self.geometryPasses.textured = False
      self.geometryPasses.visible = False
      glEnable(GL_POLYGON_OFFSET_FILL)
      glPolygonOffset(1.0, self.offset)
      glCullFace(GL_FRONT)
      glEnable( GL_CULL_FACE )
      self.drawScene( mode, lightModel )
      self.closeShadowContext( texture )
      return texture, textureMatrix
    finally:
      glDisable(GL_POLYGON_OFFSET_FILL)
      glShadeModel( GL_SMOOTH )
      glCullFace(GL_BACK)
      glDisable( GL_CULL_FACE )
      glColorMask( 1,1,1,1 )
      glPopAttrib()

  BIAS_MATRIX = array([
    [0.5, 0.0, 0.0, 0.0],
    [0.0, 0.5, 0.0, 0.0],
    [0.0, 0.0, 0.5, 0.0],
    [0.5, 0.5, 0.5, 1.0],
  ], 'f')
  shadowMapSize = 512
  textureCacheKey = 'shadowTexture'

  def setupShadowContext( self, light=None, mode=None ):
    """Create a shadow-rendering context/texture"""
    shadowMapSize = self.shadowMapSize
    texture = mode.cache.getData(light,key=self.textureCacheKey)
    if not texture:
      texture = glGenTextures( 1 )
      glBindTexture( GL_TEXTURE_2D, texture )
      glTexImage2D(
        GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
        shadowMapSize, shadowMapSize, 0,
        GL_DEPTH_COMPONENT, GL_UNSIGNED_BYTE, None
      )
    holder = mode.cache.holder( light,texture,key=self.textureCacheKey)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glViewport( 0,0, shadowMapSize, shadowMapSize )
    return texture

  def closeShadowContext( self, texture ):
    """Close our shadow-rendering context/texture"""
    shadowMapSize = self.shadowMapSize
    glBindTexture(GL_TEXTURE_2D, texture)
    glCopyTexSubImage2D(
      GL_TEXTURE_2D, 0, 0, 0, 0, 0, shadowMapSize, shadowMapSize
    )
    return texture

  def renderAmbient( self, mode ):
    """Render ambient-only lighting for geometry"""
    self.geometryPasses.context = self
    self.geometryPasses.cache = mode.cache
    self.geometryPasses.visible = True
    self.geometryPasses.lighting = True
    self.geometryPasses.lightingAmbient = True
    self.geometryPasses.lightingDiffuse = False
    self.geometryPasses.textured = True
    for i,light in enumerate( self.lights ):
      light.Light( GL_LIGHT0+i, mode=self.geometryPasses )
    self.drawScene( mode, mode.getModelView() )

  def renderDiffuse( self, light, texture, textureMatrix, mode, id=0 ):
    """Render lit-pass for given light"""
    self.geometryPasses.lightingAmbient = False
    self.geometryPasses.lightingDiffuse = True
    light.Light( GL_LIGHT0 + id, mode=self.geometryPasses )
    texGenData = [
      (GL_S,GL_TEXTURE_GEN_S,textureMatrix[0]),
      (GL_T,GL_TEXTURE_GEN_T,textureMatrix[1]),
      (GL_R,GL_TEXTURE_GEN_R,textureMatrix[2]),
      (GL_Q,GL_TEXTURE_GEN_Q,textureMatrix[3]),
    ]
    for token,gen_token,row in texGenData:
      glTexGeni(token, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
      glTexGenfv(token, GL_EYE_PLANE, row )
      glEnable(gen_token)
    glBindTexture(GL_TEXTURE_2D, texture)
    glEnable(GL_TEXTURE_2D)
    glTexParameteri(
      GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE,
      GL_COMPARE_R_TO_TEXTURE
    )
    glTexParameteri(
      GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL
    )
    glTexParameteri(
      GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_ALPHA
    )
    glAlphaFunc(GL_GEQUAL, .99)
    glEnable(GL_ALPHA_TEST)
    try:
      return self.drawScene( mode, mode.getModelView() )
    finally:
      glDisable(GL_TEXTURE_2D)
      for _,gen_token,_ in texGenData:
        glDisable(gen_token)
      glDisable(GL_LIGHTING)
      glDisable(GL_LIGHT0+id)
      glDisable(GL_ALPHA_TEST)
      mode.lightingAmbient = True
      glTexParameteri(
        GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE,
        GL_NONE
      )

if __name__ == "__main__":
  TestContext.ContextMainLoop(
    size = (512,512),
  )
