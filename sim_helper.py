import bpy
from . import helper, constant


def get_internal_collection(name, sibling):
    collection = sibling.users_collection[0]

    if name in collection.children.keys():
        return collection.children[name]
    else:
        internal_collection = bpy.data.collections.new(name)
        collection.children.link(internal_collection)
        internal_collection.hide_viewport = True
        return internal_collection


def find_siblings_by_type(obj, cut_types, collection=None):
    if not collection:
        collection = obj.users_collection[0]

    cutables = [o for o in collection.objects if o.type in ['MESH', 'CURVE']]
    return [o for o in cutables if o.soc_cut_type in cut_types]


def perimeter_thickness(obj):
    perimeters = find_siblings_by_type(obj, ['Perimeter'])

    if perimeters:
        return perimeters[0].soc_cut_depth

    else:
        return 10.0  # TODO unit


def delete_modifier(obj, name):
    if name in obj.modifiers.keys():
        obj.modifiers.remove(obj.modifiers[name])


def delete_modifiers(obj):
    for modifier in obj.modifiers:
        if modifier.name.startswith(constant.prefix):
            obj.modifiers.remove(modifier)


def delete_internal_objects(obj):
    collection = obj.users_collection[0]
    if constant.prefix + 'internal' in collection.children.keys():
        internal_collection = collection.children[constant.prefix + 'internal']
        [bpy.data.objects.remove(o, do_unlink=True) for o in internal_collection.objects if
         o.name.startswith(constant.prefix + obj.name)]


def cleanup(context, obj):
    delete_modifiers(obj)
    delete_internal_objects(obj)
    obj.display_type = 'TEXTURED'

    cleanup_boolean_modifiers(context, obj)

    if obj.type == 'CURVE':
        obj.data.bevel_object = None


def find_perimeters(context, collection):
    all_perimeters = find_siblings_by_type(context.object, 'Perimeter', collection)
    return [o for o in all_perimeters if o.name in collection.objects.keys()]


def adjust_boolean_modifiers(context, collection, target_obj):
    for perimeter_obj in find_perimeters(context, collection):
        rebuild_boolean_modifier(perimeter_obj, target_obj)


def boolean_modifier_name(cut_obj):
    return constant.prefix + "Boolean." + cut_obj.name


def cleanup_boolean_modifiers(context, target_obj):
    collection = target_obj.users_collection[0]
    for perimeter in find_perimeters(context, collection):
        delete_modifier(perimeter, boolean_modifier_name(target_obj))


def rebuild_boolean_modifier(obj, target_obj):
    modifier_name = boolean_modifier_name(target_obj)
    delete_modifier(obj, modifier_name)
    boolean = obj.modifiers.new(modifier_name, 'BOOLEAN')
    boolean.operation = 'DIFFERENCE'
    boolean.object = helper.get_object_safely(target_obj.name)
