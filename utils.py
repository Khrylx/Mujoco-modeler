import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from common import *
from geometry import Ray


def get_ray_from_screen(x, y):
    model_mat = glGetDoublev(GL_MODELVIEW_MATRIX)
    proj_mat = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    p1 = np.array(gluUnProject(x, viewport[3] - y - 1, 0, model_mat, proj_mat, viewport))
    p2 = np.array(gluUnProject(x, viewport[3] - y - 1, 1, model_mat, proj_mat, viewport))
    return Ray(p1, normalize(p2 - p1))
