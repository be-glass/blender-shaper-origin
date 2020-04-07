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
        return 'TODO'      # a feature missing implementation. TODO will be printed into the SVG file
    else:  # 'global'
        return obj.matrix_world @ coordinates


def move_object(obj, collection):
    [c.objects.unlink(obj) for c in obj.users_collection]
    collection.objects.link(obj)


def select_active(context, obj):
    for o in context.selected_objects:
        o.select_set(False)

    obj.select_set(True)
    context.view_layer.objects.active = obj


def error_msg(message, context=bpy.context):
    def msg(self, text):
        self.layout.label(text="Something went wrong!")

    context.window_manager.popup_menu(msg, title="Error", icon='ERROR')
    print("DEBUG me")


def err_implementation(context=bpy.context):
    error_msg("missing implementation", context)


def get_object_safely(obj_name):
    if obj_name in bpy.data.objects:
        return bpy.data.objects[obj_name]
    else:
        error_msg("Cannot find (internal) object")


def delete_object(obj_name):
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        bpy.data.objects.remove(obj, do_unlink=True)


def apply_scale():
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def apply_transformations():
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def repair_mesh(context, obj):
    active = context.object
    select_active(context, obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # approach 1
    # bpy.ops.mesh.dissolve_degenerate(threshold=0.1)  # TODO unit
    # bpy.ops.mesh.normals_make_consistent(inside=False)

    # approach 2
    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.mode_set(mode='OBJECT')

    if active:
        select_active(context, active)


def shade_mesh_flat(obj):
    for f in obj.data.polygons:
        f.use_smooth = False


def length(magnitude_with_unit):

    return bpy.utils.units.to_value(
        'METRIC',
        'LENGTH',
        magnitude_with_unit
    ) / 0.001 # mm # TODO , get scale_length, but how?


def hide_objects(name):
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.hide_set(True)

