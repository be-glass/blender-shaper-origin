from math import inf

import bpy
import itertools
from . import constant
from mathutils import Vector

def write(content, file_name):
    file = open(file_name, 'w')
    if file:
        if file.writelines(content):
            file.close()
            return True
        else:
            file.close()
    return False


def write_nested_list(nested_list, file_name):
    content = list(itertools.chain(*nested_list))
    return write(content, file_name)


def project_name():
    name = (bpy.path.display_name_from_filepath(bpy.data.filepath))
    name = name if name else "untitled"
    return name


def filter_valid(object_list, valid_types):
    return [obj for obj in object_list if obj.type in valid_types]


def check_type(obj, valid_types):
    remain = filter_valid([obj], valid_types)
    return True if remain else False


def get_material(cut_type):
    materials = bpy.data.materials
    id = constant.prefix+cut_type
    if id in materials.keys():
        m = materials[id]
    else:
        m = materials.new(id)
    m.diffuse_color = constant.cut_face_color[cut_type]
    return m


def boundaries(object_list):

    x = []
    y = []
    z = []
    for obj in object_list:
        mw = obj.matrix_world
        bb = obj.bound_box
        for p in range(7):

            v_local = Vector([bb[p][0], bb[p][1], bb[p][2]])

            v = transform_if_needed(obj, v_local)

            x.append(v[0])
            y.append(v[1])
            z.append(v[2])



    return min(x), min(y), min(z), max(x), max(y), max(z)


def add_Empty_at(*location):
    bpy.ops.object.add(type='EMPTY', location=(location))


def transform_if_needed(obj, coordinates):
    if obj.soc_reference_frame == 'local':
        return coordinates
    elif obj.soc_reference_frame == 'object':
        return 'TODO'
    else:  # 'global'
        return obj.matrix_world @ coordinates
