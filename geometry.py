from renderer import Renderer
from common import *
from lxml.etree import Element
from transformation import rotation_matrix, quaternion_matrix, \
    quaternion_about_axis, quaternion_multiply, quaternion_inverse, euler_from_quaternion, quaternion_from_euler
from OpenGL.GL import *
import math

renderer = Renderer()


class Capsule:

    def __init__(self, p1, p2, r, node=None):
        self.symm_geom = None
        self.p1 = p1.copy()
        self.p2 = p2.copy()
        self.r = r
        self.type = 'capsule'
        self.bone = None
        if node is None:
            self.node = Element('geom')
            self.sync_node(False)
        else:
            self.node = node

    def clone(self):
        return Capsule(self.p1, self.p2, self.r)

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
        self.sync_symm()

    def thicken(self, delta):
        self.r += delta
        self.sync_symm()

    def rotate(self, axis, angle):
        rot_mat = rotation_matrix(angle, axis)[:3, :3]
        e = (self.p2 - self.p1) * 0.5
        e = rot_mat.dot(e[:, None]).ravel()
        mid = (self.p1 + self.p2) * 0.5
        self.p1 = mid + e
        self.p2 = mid - e
        self.sync_symm()

    def move(self, delta):
        self.p1 += delta
        self.p2 += delta
        self.sync_symm()

    def sync_node(self, local_coord):
        p1 = self.p1 - self.bone.sp if local_coord else self.p1
        p2 = self.p2 - self.bone.sp if local_coord else self.p2
        self.node.attrib['fromto'] = '{:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f}'.format(*np.hstack([p1, p2]))
        self.node.attrib['size'] = '{:.4f}'.format(self.r)
        self.node.attrib['type'] = self.type

    def sync_symm(self):
        if self.symm_geom is not None:
            self.symm_geom.p1 = self.p1.copy()
            self.symm_geom.p2 = self.p2.copy()
            self.symm_geom.p1[0] *= -1
            self.symm_geom.p2[0] *= -1
            self.symm_geom.r = self.r


class Sphere:
    def __init__(self, pos, size, node=None):
        self.symm_geom = None
        self.pos = pos.copy()
        self.size = size
        self.type = 'sphere'
        self.bone = None
        if node is None:
            self.node = Element('geom')
            self.sync_node(False)
        else:
            self.node = node

    def clone(self):
        return Sphere(self.pos, self.size)

    @classmethod
    def from_node(cls, node):
        pos = np.fromstring(node.attrib['pos'], sep=' ')
        size = float(node.attrib['size'])
        geom = cls(pos, size, node)
        return geom

    def render(self):
        glPushMatrix()
        glTranslated(*self.pos)
        glScaled(self.size, self.size, self.size)
        renderer.render_point(np.zeros(3,), 1)
        glPopMatrix()

    def pick(self, ray):
        return ray.dist2point(self.pos) <= self.size

    def lengthen(self, delta):
        self.size += delta
        self.sync_symm()

    def move(self, delta):
        self.pos += delta
        self.sync_symm()

    def rotate(self, axis, angle):
        return

    def sync_node(self, local_coord):
        pos = self.pos - self.bone.sp if local_coord else self.pos
        self.node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(*pos)
        self.node.attrib['size'] = '{:.4f}'.format(self.size)
        self.node.attrib['type'] = self.type

    def sync_symm(self):
        if self.symm_geom is not None:
            self.symm_geom.pos = self.pos.copy()
            self.symm_geom.size = self.size
            self.symm_geom.pos[0] *= -1


class Box:
    def __init__(self, pos, size, quat=np.array([1, 0, 0, 0]), node=None):
        self.symm_geom = None
        self.pos = pos.copy()
        self.size = size.copy()
        self.quat = quat.copy()
        self.type = 'box'
        self.bone = None
        if node is None:
            self.node = Element('geom')
            self.sync_node(False)
        else:
            self.node = node

    def clone(self):
        return Box(self.pos, self.size, self.quat)

    @classmethod
    def from_node(cls, node):
        pos = np.fromstring(node.attrib['pos'], sep=' ')
        size = np.fromstring(node.attrib['size'], sep=' ')
        if 'quat' in node.attrib:
            quat = np.fromstring(node.attrib['quat'], sep=' ')
            quat = quaternion_inverse(quat)
        else:
            quat = np.array([1, 0, 0, 0])
        geom = cls(pos, size, quat, node)
        return geom

    def render(self):
        glPushMatrix()
        glTranslated(*self.pos)
        glMultMatrixd(quaternion_matrix(self.quat))
        glScaled(*self.size*2)
        renderer.render_cube(np.zeros(3,), 1)
        glPopMatrix()

    def pick(self, ray):
        return ray.dist2point(self.pos) <= self.size.mean()

    def lengthen(self, delta):
        self.size += delta
        self.sync_symm()

    def move(self, delta):
        self.pos += delta
        self.sync_symm()

    def rotate(self, axis, angle):
        self.quat = quaternion_multiply(self.quat, quaternion_about_axis(angle, axis))
        self.sync_symm()

    def sync_node(self, local_coord):
        pos = self.pos - self.bone.sp if local_coord else self.pos
        self.node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(*pos)
        self.node.attrib['size'] = '{:.4f} {:.4f} {:.4f}'.format(*self.size)
        self.node.attrib['quat'] = '{:.4f} {:.4f} {:.4f} {:.4f}'.format(*quaternion_inverse(self.quat))
        self.node.attrib['type'] = self.type

    def sync_symm(self):
        if self.symm_geom is not None:
            self.symm_geom.pos = self.pos.copy()
            self.symm_geom.size = self.size.copy()
            self.symm_geom.pos[0] *= -1
            ax, ay, az = euler_from_quaternion(self.quat)
            self.symm_geom.quat = quaternion_from_euler(ax, -ay, -az)


class Ray:

    def __init__(self, origin, direction):
        self.origin = origin.copy()
        self.direction = direction.copy()

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


