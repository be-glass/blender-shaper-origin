import bpy

from . import helper, fillet
from .constant import Prefix


def get_internal_collection(sibling):
    name = Prefix + 'internal'
    collection = sibling.users_collection[0]

    for child in collection.children:
        if child.name.startswith(name):
            return child

    # otherwise create one
    internal_collection = bpy.data.collections.new(name)
    collection.children.link(internal_collection)
    return internal_collection


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
        if modifier.name.startswith(Prefix):
            obj.modifiers.remove(modifier)


def delete_internal_objects(obj):
    collection = obj.users_collection[0]
    internal_collection = get_internal_collection(obj)
    for o in internal_collection.objects:
        # if o.name.startswith(Prefix + obj.name):
        if o.name == Prefix+obj.name+".fillets":
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup_meshes(source_obj, mesh_name):
    collection = source_obj.users_collection[0]
    internal_collection = get_internal_collection(source_obj)
    for o in internal_collection.objects:
        if o.name.startswith(mesh_name):
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup(context, obj):
    delete_modifiers(obj)
    delete_internal_objects(obj)
    obj.display_type = 'TEXTURED'

    cleanup_boolean_modifiers(context, obj)

    if obj.type == 'CURVE':
        obj.data.bevel_object = None


def find_perimeters(collection):
    all_perimeters = find_siblings_by_type('Perimeter', collection=collection)
    return [o for o in all_perimeters if o.name in collection.objects.keys()]


def boolean_modifier_name(cut_obj):
    return Prefix + "Boolean." + cut_obj.name


def cleanup_boolean_modifiers(context, target_obj):
    collection = target_obj.users_collection[0]
    for perimeter in find_perimeters(collection):
        delete_modifier(perimeter, boolean_modifier_name(target_obj))


def rebuild_boolean_modifier(perimeter_obj, subtract_obj):

    modifier_name = boolean_modifier_name(subtract_obj)
    subtract_fillet = fillet.Fillet(subtract_obj).get_obj()
    perimeter_fillet = fillet.Fillet(perimeter_obj).get_obj()

    delete_modifier(perimeter_fillet, modifier_name)
    boolean = perimeter_fillet.modifiers.new(modifier_name, 'BOOLEAN')
    boolean.operation = 'DIFFERENCE'
    boolean.object = helper.get_object_safely(subtract_fillet.name)

    subtract_fillet.hide_set(True)
