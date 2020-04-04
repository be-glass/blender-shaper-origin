import bpy
from . import helper, constant


def delete_old_cuts(obj):
    for collection in bpy.data.collections:
        for cut in all_cuts(collection):
            if cut.obj == obj:
                cut.delete()


def all_cuts(collection):
    return collection.soc_perimeters + \
           collection.soc_mesh_cuts + \
           collection.soc_curve_cuts


def get_internal_collection(name, sibling):
    first_parent = sibling.users_collection

    first_parent = helper.find_collection(sibling)[0]
    if name in first_parent.children.keys():
        return first_parent.children[name]
    else:
        collection = bpy.data.collections.new(name)
        first_parent.children.link(collection)
        collection.hide_viewport = True
        return collection


def find_siblings_by_type(obj, cut_types):
    collections = helper.find_collection(obj)
    collection = collections[0]
    objects = collection.objects
    return [o for o in objects if o.soc_cut_type in cut_types]


def perimeter_thickness(obj):
    perimeters = find_siblings_by_type(obj, ['Perimeter'])

    if perimeters:
        return perimeters[0].soc_cut_depth

    else:
        return 10.0  # TODO unit

