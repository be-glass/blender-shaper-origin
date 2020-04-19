import bmesh
import bpy
import itertools

from mathutils import Vector, Matrix

from .constant import PREFIX


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


def boundaries_in_local_coords(object_list):
    x = []
    y = []
    z = []
    for obj in object_list:
        scale = Matrix.Diagonal(obj.matrix_world.to_scale())

        bb = obj.bound_box
        for p in range(8):
            v_local = Vector([bb[p][0], bb[p][1], bb[p][2]])

            v = scale @ v_local

            x.append(v[0])
            y.append(v[1])
            z.append(v[2])

    minimum = Vector([min(x), min(y), min(z)])
    maximum = Vector([max(x), max(y), max(z)])
    return minimum, maximum


def add_Empty_at(*location):
    bpy.ops.object.add(type='EMPTY', location=(location))


def transform_if_needed(obj, coordinates):
    if obj.soc_reference_frame == 'local':
        return coordinates
    elif obj.soc_reference_frame == 'object':
        return 'TODO'  # a feature missing implementation. TODO will be printed into the SVG file
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


def warning_msg(message, context=bpy.context):
    def msg(self, text):
        self.layout.label(text="Something went wrong!")

    context.window_manager.popup_menu(msg, title="Warning", icon='WARNING')
    print("DEBUG me")


def err_implementation(context=bpy.context):
    error_msg("missing implementation", context)


def get_object_safely(obj_name, error_msg=True):
    if obj_name in bpy.data.objects.keys():
        return bpy.data.objects[obj_name]
    elif error_msg:
        error_msg("Cannot find (internal) object")
    return None


def delete_object(obj_name):
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        bpy.data.objects.remove(obj, do_unlink=True)


def apply_scale(context, obj):
    S = Matrix.Diagonal(obj.matrix_world.to_scale())

    for v in obj.data.vertices:
        v.co = S @ v.co

    obj.scale = Vector([1, 1, 1])  # TODO: Does it work at all?


def repair_mesh(context, obj):
    active = context.object
    select_active(context, obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.mode_set(mode='OBJECT')

    if active:
        select_active(context, active)


def shade_mesh_flat(obj):
    for f in obj.data.polygons:
        f.use_smooth = False


def hide_objects(name):
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.hide_set(True)


def length(context, quantity_with_unit):
    return bpy.utils.units.to_value('METRIC', 'LENGTH', quantity_with_unit) / context.scene.unit_settings.scale_length


def create_object(collection, polygon, name):
    bm = bmesh.new()
    [bm.verts.new(v) for v in polygon]
    bm.faces.new(bm.verts)
    bm.normal_update()
    me = bpy.data.meshes.new("")
    bm.to_mesh(me)
    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)
    return obj


def translate_local(obj, vector):
    rotation = obj.rotation_euler.to_matrix()
    rotation.invert()
    global_translation = vector @ rotation
    obj.location += global_translation


def add_plane(context, name, size, collection=None):
    bpy.ops.mesh.primitive_plane_add(size=size)

    # delete face
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.object.data.polygons[0].select = True
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    select_active(context, context.object)  # TODO

    obj = context.active_object
    obj.name = name

    if collection:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def get_collection(context, name, parent):
    if name in bpy.data.collections.keys():
        return bpy.data.collections[name]
    else:
        collection = bpy.data.collections.new(name)
        parent.children.link(collection)
        return collection


def get_soc_collection(context):
    return get_collection(context, "SOC", context.scene.collection)


def get_preview_collection(context):
    soc = get_soc_collection(context)
    return get_collection(context, "Preview", soc)


def get_internal_collection(sibling):
    name = PREFIX + 'internal'
    collection = sibling.users_collection[0]

    for child in collection.children:
        if child.name.startswith(name):
            return child

    # otherwise create one
    internal_collection = bpy.data.collections.new(name)
    collection.children.link(internal_collection)
    return internal_collection
