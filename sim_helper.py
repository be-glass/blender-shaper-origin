import bpy
from . import helper, constant


def get_internal_collection(name, sibling):
    first_parent = helper.find_collection(sibling)[0]
    if name in first_parent.children.keys():
        return first_parent.children[name]
    else:
        collection = bpy.data.collections.new(name)
        first_parent.children.link(collection)
        collection.hide_viewport = True
        return collection


def find_siblings_by_type(obj, cut_types):
    objs = find_cutables(obj)
    return [o for o in objs if o.soc_cut_type in cut_types]


def find_cutables(obj):
    collection = obj.users_collection[0]
    return [o for o in collection.objects if o.type in ['MESH', 'CURVE']]


def find_cut_objects(context):
    cutables = find_cutables(context.object)
    return [o for o in cutables if o.soc_cut_type != 'None']


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
    if 'SOC_internal' in collection.children.keys():
        internal_collection = collection.children['SOC_internal']
        [bpy.data.objects.remove(o, do_unlink=True) for o in internal_collection.objects if
         o.name.startswith("SOC_" + obj.name)]


def cleanup(context, obj):
    delete_modifiers(obj)
    delete_internal_objects(obj)
    obj.display_type = 'TEXTURED'
    cleanup_boolean_modifiers(context, obj)

def perimeters(context):
    collection = context.object.users_collection[0]
    all_perimeters = find_siblings_by_type(context.object, 'Perimeter')
    return [o for o in all_perimeters if o.name in collection.objects.keys()]


def adjust_boolean_modifiers(context, target_obj):
    for perimeter in perimeters(context):
        rebuild_boolean_modifier(perimeter, target_obj)


def boolean_modifier_name(cut_obj):
    return "SOC_Boolean." + cut_obj.name

def cleanup_boolean_modifiers(context, target_obj):
    for perimeter in perimeters(context):
        delete_modifier(perimeter, boolean_modifier_name(target_obj))


def rebuild_boolean_modifier(obj, cut):
    modifier_name = boolean_modifier_name(cut)

    delete_modifier(obj, modifier_name)
    boolean = obj.modifiers.new(modifier_name, 'BOOLEAN')
    boolean.operation = 'DIFFERENCE'

    if cut.soc_cut_type in ['Cutout', 'Pocket']:
        boolean.object = cut

    elif cut.soc_cut_type in ['Exterior', 'Interior', 'Online']:
        mesh_name = f'SOC_{cut.name}.mesh'
        boolean.object = helper.get_object_safely(mesh_name)
    else:
        helper.err_implementation()
