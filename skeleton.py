from lxml.etree import parse, ElementTree, Element, SubElement
import numpy as np


class Cylinder:

    def __init__(self, p1, p2, r):
        self.p1 = p1
        self.p2 = p2
        self.r = r


class Bone:

    def __init__(self, node):
        self.name = ''
        self.sp = None  # start point
        self.ep = None  # end point
        self.mp = None  # mid point
        self.geoms = []
        self.node = node


class Skeleton:

    def __init__(self, xml_file):
        self.bones = []
        self.tree = None
        self.load_from_xml(xml_file)

    def load_from_xml(self, xml_file):
        self.tree = parse(xml_file)
        root = self.tree.getroot().find('worldbody').find('body')
        self.add_bones(root, None)

    def add_bones(self, bone_node, parent_bone):
        bone = Bone(bone_node)
        bone.name = bone_node.attrib['name']
        bone.ep = np.fromstring(bone_node.attrib['end'], sep=' ')
        if parent_bone is not None:
            bone.sp = parent_bone.ep.copy()
        else:
            bone.sp = bone.ep.copy()
        bone.mp = 0.5 * (bone.sp + bone.ep)
        self.bones.append(bone)

        for bone_node_c in bone_node.findall('body'):
            self.add_bones(bone_node_c, bone)
