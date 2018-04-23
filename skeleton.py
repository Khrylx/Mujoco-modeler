from lxml.etree import XMLParser, parse, ElementTree, Element, SubElement
from OpenGL.GL import *
from geometry import Capsule, Ellipsoid, Box, renderer
from utils import *
import numpy as np


class Bone:

    def __init__(self, node, parent_bone):
        self.geoms = []
        self.node = node
        self.symm_bone = None
        self.is_picked = False
        self.picked_geom = None
        self.parent = parent_bone
        self.name = node.attrib['name']
        self.ep = np.fromstring(node.attrib['user'], sep=' ')
        if parent_bone is not None:
            self.sp = parent_bone.ep.copy()
        else:
            self.sp = self.ep.copy()
        self.mp = 0.5 * (self.sp + self.ep)
        # add geometries
        for geom_node in node.findall('geom'):
            geom_type = geom_node.attrib['type']
            if geom_type == 'capsule':
                self.geoms.append(Capsule.from_node(geom_node))
            elif geom_type == 'ellipsoid':
                self.geoms.append(Ellipsoid.from_node(geom_node))
            elif geom_type == 'box':
                self.geoms.append(Box.from_node(geom_node))
            self.geoms[-1].bone = self

    def __str__(self):
        return self.name

    def render(self, render_options):
        if render_options['render_bone']:
            color = [1.0, 0.0, 0.0] if self.is_picked else [0.8, 0.8, 0.8]
            glColor3d(*color)
            renderer.render_point(self.ep, 0.022)
            renderer.render_capsule(self.sp, self.ep, 0.02)
        if render_options['render_geom']:
            for geom in self.geoms:
                color = [0.0, 1.0, 0.0] if geom == self.picked_geom else [1.0, 0.65, 0.0]
                glColor3d(*color)
                geom.render()

    def pick(self, ray):
        for geom in self.geoms:
            res = geom.pick(ray)
            if res:
                self.picked_geom = geom
                self.is_picked = True
                return geom
        if ray.dist2seg(self.sp, self.ep) < 0.02:
            self.is_picked = True
        return None

    def sync_node(self, local_coord):
        for geom in self.geoms:
            geom.sync_node(local_coord)

        if local_coord and self.name != 'root':
            self.node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(*(self.sp - self.parent.sp))
            self.node.attrib['user'] = '{:.4f} {:.4f} {:.4f}'.format(0, 0, 0)
            for j_node in self.node.findall('joint'):
                j_node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(0, 0, 0)

        # self.node.attrib['user'] = '{:.4f} {:.4f} {:.4f}'.format(*self.ep)
        # self.node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(*self.mp)
        # for j_node in self.node.findall('joint'):
        #     j_node.attrib['pos'] = '{:.4f} {:.4f} {:.4f}'.format(*self.sp)
        #     if self.name != 'root':
        #         j_node.attrib['armature'] = '0.01'
        #         j_node.attrib['stiffness'] = '1.0'
        #         j_node.attrib['damping'] = '5.0'

    def delete_geom(self):
        symm_geom = self.picked_geom.symm_geom
        self.node.remove(self.picked_geom.node)
        self.geoms.remove(self.picked_geom)
        if self.symm_bone is not None:
            self.symm_bone.node.remove(symm_geom.node)
            self.symm_bone.geoms.remove(symm_geom)
        self.picked_geom = None

    def add_geom(self, geom_type='capsule', bone_capsule=False, clone_picked=False):
        geom = symm_geom = None
        if clone_picked:
            geom = self.picked_geom.clone()
            symm_geom = self.picked_geom.clone()
        elif geom_type == 'capsule':
            if bone_capsule:
                p1 = self.sp.copy()
                p2 = self.ep.copy()
            else:
                p1 = self.mp.copy()
                p2 = self.mp.copy()
                p1[0] -= 0.03
                p2[0] += 0.03
            geom = Capsule(p1, p2, 0.025)
            if self.symm_bone is not None:
                symm_geom = Capsule(p1, p2, 0.025)
        elif geom_type == 'ellipsoid':
            geom = Ellipsoid(self.mp, np.ones(3, ) * 0.04)
            if self.symm_bone is not None:
                symm_geom = Ellipsoid(self.mp, np.ones(3, ) * 0.04)
        elif geom_type == 'box':
            geom = Box(self.mp, np.ones(3, ) * 0.04)
            if self.symm_bone is not None:
                symm_geom = Box(self.mp, np.ones(3, ) * 0.04)

        if geom is None:
            return
        self.node.insert(0, geom.node)
        self.geoms.append(geom)
        if self.symm_bone is not None:
            self.symm_bone.node.insert(0, symm_geom.node)
            self.symm_bone.geoms.append(symm_geom)
            symm_geom.symm_geom = geom
            geom.symm_geom = symm_geom
            geom.sync_symm()
        self.picked_geom = geom

    def sync_symm(self):
        self.symm_bone.sp = self.sp.copy()
        self.symm_bone.mp = self.mp.copy()
        self.symm_bone.ep = self.ep.copy()
        self.symm_bone.sp[0] *= -1
        self.symm_bone.mp[0] *= -1
        self.symm_bone.ep[0] *= -1
        for geom in self.geoms:
            geom.sync_symm()


class Skeleton:

    def __init__(self, xml_file):
        self.bones = []
        self.tree = None
        self.picked_geom = None
        self.picked_bone = None
        self.load_from_xml(xml_file)

    def load_from_xml(self, xml_file):
        parser = XMLParser(remove_blank_text=True)
        self.tree = parse(xml_file, parser=parser)
        root = self.tree.getroot().find('worldbody').find('body')
        self.add_bones(root, None)
        self.build_symm()
        self.make_symm()

    def save_to_xml(self, xml_file, local_coord=False):
        for bone in self.bones:
            bone.sync_node(local_coord)
        self.tree.write(xml_file, pretty_print=True)

    def add_bones(self, bone_node, parent_bone):
        bone = Bone(bone_node, parent_bone)
        self.bones.append(bone)

        for bone_node_c in bone_node.findall('body'):
            self.add_bones(bone_node_c, bone)

    def build_symm(self):
        for bone_a in self.bones:
            for bone_b in self.bones:
                if bone_a != bone_b and bone_a.name[1:] == bone_b.name[1:]:
                    bone_a.symm_bone = bone_b
                    for i, geom in enumerate(bone_a.geoms):
                        geom.symm_geom = bone_b.geoms[i]

    def make_symm(self):
        for i, bone in enumerate(self.bones):
            if bone.symm_bone is not None and self.bones.index(bone.symm_bone) > i:
                bone.sync_symm()

    def render(self, render_options):
        for bone in self.bones:
            bone.render(render_options)

    def pick_geom(self, ray):
        self.picked_geom = None
        self.picked_bone = None
        for bone in self.bones:
            bone.picked_geom = None
            bone.is_picked = False

        for bone in self.bones:
            res = bone.pick(ray)
            if bone.is_picked:
                self.picked_bone = bone
                if res is not None:
                    self.picked_geom = res
                return True
        return False



