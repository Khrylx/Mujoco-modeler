from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

# -----------
# VARIABLES
# -----------

g_fViewDistance = 9.
g_Width = 600
g_Height = 600

g_nearPlane = 1.
g_farPlane = 1000.

g_button = None
x_start = 0
y_start = 0

# camera parameters
zoom = 20.
up = 1.
theta = 90.
phi = 0.
center_x = 0
center_y = 0
center_z = 0

# -------------------
# SCENE CONSTRUCTOR
# -------------------


def draw_scene():
    glutSolidTeapot(1.)


# --------
# VIEWER
# --------


def init():
    glEnable(GL_NORMALIZE)
    glLightfv(GL_LIGHT0, GL_POSITION, [.0, 10.0, 10., 0.])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [.0, .0, .0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)


def display():
    # Clear frame buffer and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    # Render the scene
    draw_scene()
    # Make sure changes appear onscreen
    glutSwapBuffers()


def update_cam():
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(zoom * math.cos(math.radians(phi)) * math.cos(math.radians(theta)) + center_x,
              zoom * math.sin(math.radians(phi)) + center_y,
              zoom * math.cos(math.radians(phi)) * math.sin(math.radians(theta)) + center_z, center_x, center_y,
              center_z, 0.0, up, 0.0)


def reshape(width, height):
    global g_Width, g_Height
    g_Width = width
    g_Height = height
    glViewport(0, 0, g_Width, g_Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(zoom, float(g_Width) / float(g_Height), g_nearPlane, g_farPlane)
    update_cam()


def keyboard(key, x, y):
    if key == 'q':
        exit(0)
    glutPostRedisplay()


def mouse(button, state, x, y):
    global g_button, x_start, y_start
    if state == GLUT_DOWN:
        g_button = button
        x_start = x
        y_start = y


def motion(x, y):
    global g_button, zoom, x_start, y_start, phi, theta, up
    if g_button == GLUT_LEFT_BUTTON:
        theta += (x - x_start) * up
        phi += (y - y_start) * up
        if phi > 90:
            theta += 180
            phi = 180 - phi
            up = -up
        if phi < -90:
            theta += 180
            phi = -180 - phi
            up = -up
    if g_button == GLUT_RIGHT_BUTTON:
        if math.fabs(y-y_start) > 1:
            zoom += (y - y_start) / 10
            zoom = max(zoom, 5)

    update_cam()
    x_start = x
    y_start = y
    glutPostRedisplay()


# ------
# MAIN
# ------
if __name__ == "__main__":
    # GLUT Window Initialization
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # zBuffer
    glutInitWindowSize(g_Width, g_Height)
    glutInitWindowPosition(0 + 4, int(g_Height/4))
    glutCreateWindow("Mujoco Modeler")
    # Initialize OpenGL graphics state
    init()
    # Register callbacks
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    # Turn the flow of control over to GLUT
    glutMainLoop()
