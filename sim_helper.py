import bpy
from . import helper, constant


def delete_old_cuts(context, obj):
    for cut in context.scene.soc_cut_list:
        if cut.obj == obj:
            cut.delete(context)


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
