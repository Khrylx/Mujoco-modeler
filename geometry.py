from renderer import Renderer
from common import *
from lxml.etree import Element
from transformation import rotation_matrix, quaternion_matrix, quaternion_about_axis, quaternion_multiply, quaternion_inverse
from OpenGL.GL import *
import math

renderer = Renderer()


class Capsule:

    def __init__(self, p1, p2, r, node=None):
        self.p1 = p1
        self.p2 = p2
        self.r = r
        self.type = 'capsule'
        if node is None:
            self.node = Element('geom')
            self.sync_node()
        else:
            self.node = node

    @classmethod
    def from_node(cls, node):
        from_to = np.fromstring(node.attrib['fromto'], sep=' ')
        geom = cls(from_to[:3], from_to[3:], float(node.attrib['size']), node)
        return geom

    def render(self):
        renderer.render_capsule(self.p1, self.p2, self.r)

    def pick(self, ray):
        return ray.dist2seg(self.p1, self.p2) <= self.r

    def lengthen(self, delta):
        v = normalize(self.p2 - self.p1)
        self.p2 += 0.5 * delta * v
        self.p1 -= 0.5 * delta * v

    def rotate(self, axis, angle):
        rot_mat = rotation_matrix(angle, axis)[:3, :3]
        e = (self.p2 - self.p1) * 0.5
        e = rot_mat.dot(e[:, None]).ravel()
        mid = (self.p1 + self.p2) * 0.5
        self.p1 = mid + e
        self.p2 = mid - e

    def move(self, delta):
        self.p1 += delta
        self.p2 += delta

    def sync_node(self):
        self.node.attrib['fromto'] = '{:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f}'.format(*np.hstack([self.p1, self.p2]))
        self.node.attrib['size'] = '{:.4f}'.format(self.r)
        self.node.attrib['type'] = self.type


class Ellipsoid:
    def __init__(self, pos, size, quat=np.array([1, 0, 0, 0]), node=None):
        self.pos = pos
        self.size = size
        self.quat = quat
        self.type = 'ellipsoid'
        if node is None:
            self.node = Element('geom')
            self.sync_node()
        else:
            self.node = node

    @classmethod
    def from_node(cls, node):
        pos = np.fromstring(node.attrib['pos'], sep=' ')
        size = np.fromstring(node.attrib['size'], sep=' ')
        if 'quat' in node.attrib:
            quat = np.fromstring(node.attrib['quat'], sep=' ')
        else:
            quat = np.array([1, 0, 0, 0])
        geom = cls(pos, size, quat, node)
        return geom

    def render(self):
        glPushMatrix()
        glTranslated(*self.pos)
        glMultMatrixd(quaternion_matrix(self.quat))
        glScaled(*self.size)
        renderer.render_point(np.zeros(3,), 1)
        glPopMatrix()

    def pick(self, ray):
        return ray.dist2point(self.pos) <= self.size.mean()

    def lengthen(self, delta):
        self.size += delta

    def move(self, delta):
        self.pos += delta

    def rotate(self, axis, angle):
        self.quat = quaternion_multiply(self.quat, quaternion_about_axis(angle, axis))

    def sync_node(self):
        self.node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(*self.pos)
        self.node.attrib['size'] = '{:.4f} {:.4f} {:.4f}'.format(*self.size)
        self.node.attrib['quat'] = '{:.4f} {:.4f} {:.4f} {:.4f}'.format(*quaternion_inverse(self.quat))
        self.node.attrib['type'] = self.type


class Ray:

    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def get_point_at(self, t):
        return self.origin + self.direction * t

    def dist2point(self, p):
        t = self.direction.dot(p - self.origin)
        p_close = self.get_point_at(t)
        return norm(p - p_close)

    def dist2seg(self, p1, p2):
        u = self.origin + self.direction * 1e5 - p1
        v = p2 - p1
        w = self.origin - p1
        a = u.dot(u)
        b = u.dot(v)
        c = v.dot(v)
        d = u.dot(w)
        e = v.dot(w)
        denom = a*c - b*b
        sN = sD = tN = tD = denom

        if denom < 1e-8:
            sN = 0
            sD = 1
            tN = e
            tD = c
        else:
            sN = b*e - c*d
            tN = a*e - b*d
            if sN < 0:
                sN = 0
                tN = e
                tD = c

        if tN < 0:
            tN = 0
            if d > 0:
                sN = 0
            elif d < -a:
                sN = sD
            else:
                sN = -d
                sD = a
        elif tN > tD:
            tN = tD
            if -d + b < 0:
                sN = 0
            elif -d + b > a:
                sN = sD
            else:
                sN = -d + b
                sD = a

        sc = 0 if math.fabs(sN) < 1e-8 else sN / sD
        tc = 0 if math.fabs(tN) < 1e-8 else tN / tD

        return norm(w + u*sc - v*tc)


