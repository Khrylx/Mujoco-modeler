from renderer import Renderer
from common import *
from transformation import rotation_matrix
import math

renderer = Renderer()


class Capsule:

    def __init__(self, node):
        from_to = np.fromstring(node.attrib['fromto'], sep=' ')
        self.p1 = from_to[:3]
        self.p2 = from_to[3:]
        self.r = float(node.attrib['size'])
        self.node = node
        self.type = 'capsule'

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

    def sync_node(self):
        self.node.attrib['fromto'] = '{:.4f} {:.4f} {:.4f} {:.4f} {:.4f} {:.4f}'.format(*np.hstack([self.p1, self.p2]))
        self.node.attrib['size'] = '{:.4f}'.format(self.r)


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


