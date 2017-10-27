from OpenGL.GLUT import *
from skeleton import Skeleton
from renderer import Renderer
from utils import *
import math
import argparse

parser = argparse.ArgumentParser(description='Mujoco Modeler')
parser.add_argument('--input', default="data/my_humanoid.xml", metavar='G',
                    help='input path of the model')
parser.add_argument('--output', default="data/my_humanoid.xml", metavar='G',
                    help='output path of the model')
args = parser.parse_args()

# -----------
# VARIABLES
# -----------

g_fViewDistance = 9.
g_Width = 800
g_Height = 800

g_nearPlane = 0.01
g_farPlane = 1000.

g_button = None
x_start = 0
y_start = 0

# camera parameters
zoom = 12.
up = 1.
theta = -90.
phi = 0.
center_x = 0
center_y = 0
center_z = 0

axis_x = np.array([1.0, 0.0, 0.0])
axis_y = np.array([0.0, 1.0, 0.0])
axis_z = np.array([0.0, 0.0, 1.0])

# global variable
skeleton = None
renderer = Renderer()

# -------------------
# SCENE CONSTRUCTOR
# -------------------


def draw_scene():
    skeleton.render()
    glColor3d(1, 0, 0)

# --------
# VIEWER
# --------


def init():
    glClearColor(1.0, 1.0, 1.0, 1.0)
    # lighting
    glEnable(GL_NORMALIZE)
    glLightfv(GL_LIGHT0, GL_POSITION, [.0, 10.0, 10., 0.])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [.0, .0, .0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    # blending
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # misc
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)


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
              zoom * math.cos(math.radians(phi)) * math.sin(math.radians(theta)) + center_y,
              zoom * math.sin(math.radians(phi)) + center_z, center_x, center_y,
              center_z, 0.0, 0.0, up)


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
    key = key.decode()
    geom = skeleton.picked_geom
    rot_angle = 10
    trans_dist = 0.002
    d_size = 0.002
    if key == '`':
        exit(0)
    elif key == 'v':
        skeleton.save_to_xml(args.output)

    # rotate geometry
    elif key == 'a':
        if geom is not None:
            geom.rotate(axis_y, math.radians(rot_angle))
    elif key == 'd':
        if geom is not None:
            geom.rotate(axis_y, math.radians(-rot_angle))
    elif key == 'w':
        if geom is not None:
            geom.rotate(axis_x, math.radians(rot_angle))
    elif key == 's':
        if geom is not None:
            geom.rotate(axis_x, math.radians(-rot_angle))
    elif key == 'q':
        if geom is not None:
            geom.rotate(axis_z, math.radians(rot_angle))
    elif key == 'e':
        if geom is not None:
            geom.rotate(axis_z, math.radians(-rot_angle))

    # translate or change size
    elif key == 'j':
        if geom is not None:
            geom.move(np.array([-trans_dist, 0, 0]))
    elif key == 'l':
        if geom is not None:
            geom.move(np.array([trans_dist, 0, 0]))
    elif key == 'i':
        if geom is not None:
            geom.move(np.array([0, 0, trans_dist]))
    elif key == 'k':
        if geom is not None:
            geom.move(np.array([0, 0, -trans_dist]))
    elif key == 'u':
        if geom is not None:
            geom.move(np.array([0, trans_dist, 0]))
    elif key == 'o':
        if geom is not None:
            geom.move(np.array([0, -trans_dist, 0]))

    # change size for ellipsoid
    elif key == 'J':
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(np.array([-d_size, 0, 0]))
    elif key == 'L':
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(np.array([d_size, 0, 0]))
    elif key == 'I':
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(np.array([0, 0, d_size]))
    elif key == 'K':
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(np.array([0, 0, -d_size]))
    elif key == 'U':
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(np.array([0, d_size, 0]))
    elif key == 'O':
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(np.array([0, -d_size, 0]))

    # new geometry
    elif key == 'r':
        if skeleton.picked_bone is not None:
            skeleton.picked_bone.add_geom('capsule')
    elif key == 't':
        if skeleton.picked_bone is not None:
            skeleton.picked_bone.add_geom('ellipsoid')
    # delete geometry
    elif key == 'x':
        if geom is not None:
            skeleton.picked_bone.delete_geom()
            skeleton.picked_geom = None
    glutPostRedisplay()


def special(key, x, y):
    geom = skeleton.picked_geom
    if key == GLUT_KEY_UP:
        if geom is not None and geom.type == 'capsule':
            geom.r += 0.001
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(0.005)
    elif key == GLUT_KEY_DOWN:
        if geom is not None and geom.type == 'capsule':
            geom.r -= 0.001
        if geom is not None and geom.type == 'ellipsoid':
            geom.lengthen(-0.005)
    elif key == GLUT_KEY_RIGHT:
        if geom is not None and geom.type == 'capsule':
            geom.lengthen(0.005)
    elif key == GLUT_KEY_LEFT:
        if geom is not None and geom.type == 'capsule':
            geom.lengthen(-0.005)
    glutPostRedisplay()


def mouse(button, state, x, y):
    global g_button, x_start, y_start
    if state == GLUT_DOWN:
        g_button = button
        x_start = x
        y_start = y

        if button == GLUT_RIGHT_BUTTON:
            mouse_ray = get_ray_from_screen(x, y)
            skeleton.pick_geom(mouse_ray)
            glutPostRedisplay()


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


def init_skeleton():
    global skeleton
    xml_file = args.input
    skeleton = Skeleton(xml_file)


# ------
# MAIN
# ------
if __name__ == "__main__":
    # GLUT Window Initialization
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # zBuffer
    glutInitWindowSize(g_Width, g_Height)
    glutInitWindowPosition(200, 0)
    glutCreateWindow("Mujoco Modeler")
    # Initialize OpenGL graphics state
    init()
    # set up skeleton
    init_skeleton()
    # Register callbacks
    glutReshapeFunc(reshape)
    glutDisplayFunc(display)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special)
    # Turn the flow of control over to GLUT
    glutMainLoop()
