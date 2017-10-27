from lxml.etree import parse, ElementTree, Element, SubElement
from OpenGL.GL import *
from geometry import Capsule, renderer
from utils import *
import numpy as np


class Bone:

    def __init__(self, node, parent_bone):
        self.geoms = []
        self.picked_geom = None
        self.name = node.attrib['name']
        self.ep = np.fromstring(node.attrib['end'], sep=' ')
        if parent_bone is not None:
            self.sp = parent_bone.ep.copy()
        else:
            self.sp = self.ep.copy()
        self.mp = 0.5 * (self.sp + self.ep)
        # add geometries
        for geom_node in node.findall('geom'):
            geom_type = geom_node.attrib['type']
            if geom_type == 'capsule':
                self.geoms.append(Capsule(geom_node))

    def render(self):
        glColor3d(0.8, 0.8, 0.8)
        renderer.render_point(self.ep, 0.022)
        renderer.render_capsule(self.sp, self.ep, 0.02)
        for geom in self.geoms:
            color = [0.0, 1.0, 0.0] if geom == self.picked_geom else [1.0, 0.65, 0.0]
            glColor3d(*color)
            geom.render()

    def pick_geom(self, ray):
        for geom in self.geoms:
            res = geom.pick(ray)
            if res:
                self.picked_geom = geom
                return geom
        return None

    def sync_node(self):
        for geom in self.geoms:
            geom.sync_node()


class Skeleton:

    def __init__(self, xml_file):
        self.bones = []
        self.tree = None
        self.picked_geom = None
        self.picked_bone = None
        self.load_from_xml(xml_file)

    def load_from_xml(self, xml_file):
        self.tree = parse(xml_file)
        root = self.tree.getroot().find('worldbody').find('body')
        self.add_bones(root, None)

    def save_to_xml(self, xml_file):
        for bone in self.bones:
            bone.sync_node()
        self.tree.write(xml_file, pretty_print=True)

    def add_bones(self, bone_node, parent_bone):
        bone = Bone(bone_node, parent_bone)
        self.bones.append(bone)

        for bone_node_c in bone_node.findall('body'):
            self.add_bones(bone_node_c, bone)

    def render(self):
        for bone in self.bones:
            bone.render()

    def pick_geom(self, ray):
        self.picked_geom = None
        for bone in self.bones:
            bone.picked_geom = None

        for bone in self.bones:
            res = bone.pick_geom(ray)
            if res is not None:
                self.picked_geom = res
                self.picked_bone = bone
                return True
        return False



