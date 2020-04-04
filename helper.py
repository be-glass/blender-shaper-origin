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


# def get_material(cut_type):
#     materials = bpy.data.materials
#     id = constant.prefix+cut_type
#     if id in materials.keys():
#         m = materials[id]
#     else:
#         m = materials.new(id)
#     m.diffuse_color = constant.cut_face_color[cut_type]
#     return m


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


# def add_rectangle_curve_at():
#     bpy.ops.mesh.primitive_plane_add(size=1.0)


# howto create a curve:
# https://blender.stackexchange.com/questions/61266/creating-curves-in-pythonc = bpy.data.curves.new('new1', type='CURVE')
# curve = bpy.data.objects.new('curve1', c)
# bpy.context.scene.collection.objects.link(curve)


def transform_if_needed(obj, coordinates):
    if obj.soc_reference_frame == 'local':
        return coordinates
    elif obj.soc_reference_frame == 'object':
        return 'TODO'
    else:  # 'global'
        return obj.matrix_world @ coordinates


def find_collection(obj):
    # return [c for c in bpy.data.collections if obj.name in c.objects.keys()]
    return obj.users_collection


def move_object(obj, collection):
    [c.objects.unlink(obj) for c in obj.users_collection]
    collection.objects.link(obj)


def select_active(context, obj):

    for o in context.selected_objects:
        o.select_set(False)

    obj.select_set(True)
    context.view_layer.objects.active = obj




def error_msg(message, context = bpy.context):
    def msg(self, text):
        self.layout.label(text="Something went wrong!")
    context.window_manager.popup_menu(msg, title="Error", icon='ERROR')
    print("DEBUG me")


def err_implementation(context = bpy.context):
    error_msg("missing implementation", context)


def get_object_safely(obj_name):
    if obj_name in bpy.data.objects:
        return bpy.data.objects[obj_name]
    else:
        error_msg("Cannot find (internal) object")
