import bpy

from .helper import get_solid_collection
from . import helper
from .constant import PREFIX


def find_siblings_by_type(cut_types, sibling=None, collection=None):
    if not (sibling or collection):
        return []

    if not collection:
        collection = sibling.users_collection[0]

    cutables = [o for o in collection.objects if o.type in ['MESH', 'CURVE']]
    return [o for o in cutables if (o.soc_mesh_cut_type in cut_types) or (o.soc_curve_cut_type in cut_types)]


def perimeter_thickness(obj):
    perimeters = find_siblings_by_type(['Perimeter'], sibling=obj)
    if perimeters:
        return perimeters[0].soc_cut_depth
    else:
        return None


def delete_modifier(obj, name):
    if name in obj.modifiers.keys():
        obj.modifiers.remove(obj.modifiers[name])


def delete_modifiers(obj):
    for modifier in obj.modifiers:
        if modifier.name.startswith(PREFIX):
            obj.modifiers.remove(modifier)


def delete_solid_objects(context, obj):
    solid_collection = get_solid_collection(context)
    for o in solid_collection.objects:
        if o.name == PREFIX + obj.name + ".fillets":
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup_meshes(context, source_obj, mesh_name):
    solid_collection = get_solid_collection(context)
    for o in solid_collection.objects:
        if o.name.startswith(mesh_name):
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup(context, obj):
    if obj.soc_known_as != obj.name:
        return

    delete_modifiers(obj)
    delete_solid_objects(context, obj)
    obj.display_type = 'TEXTURED'

    cleanup_boolean_modifiers(context, obj)

    if obj.type == 'CURVE':
        obj.data.bevel_object = None

    helper.delete_object(obj.soc_reference_name)
    helper.delete_object(obj.soc_preview_name)
    helper.delete_object(obj.soc_solid_name)
    obj.soc_reference_name = ''
    obj.soc_preview_name = ''
    obj.soc_solid_name = ''


def find_perimeters(collection):
    all_perimeters = find_siblings_by_type('Perimeter', collection=collection)
    return [o for o in all_perimeters if o.name in collection.objects.keys()]


def boolean_modifier_name(cut_obj):
    return PREFIX + "Boolean." + cut_obj.name


def cleanup_boolean_modifiers(context, target_obj):
    collection = target_obj.users_collection[0]
    for perimeter in find_perimeters(collection):
        delete_modifier(perimeter, boolean_modifier_name(target_obj))


def get_reference(context, obj):
    collection = helper.get_reference_collection(context)

    name = obj.soc_reference_name

    if not name:
        name = PREFIX + obj.users_collection[0].name + '.reference'

    if name in bpy.data.objects.keys():
        return bpy.data.objects[name]
    else:
        reference = bpy.data.objects.new(name, None)
        reference.location = obj.location
        # reference.matrix_world = obj.matrix_world
        reference.matrix_world.identity()
        collection.objects.link(reference)
        reference.empty_display_size = 5
        reference.empty_display_type = 'PLAIN_AXES'
        reference.soc_object_type = 'Reference'
        obj.soc_reference_name = reference.name
        return reference