import bpy

from . import constant, helper


def delete_old_modifiers(obj):
    for modifier in obj.modifiers:
        if modifier.name.startswith(constant.prefix):
            obj.modifiers.remove(modifier)


def setup(obj):

    obj.display_type = 'TEXTURED'
    delete_old_modifiers(obj)


    if not obj.soc_simulate:
        return

    if obj.soc_cut_type in ['Perimeter', 'Cutout']:
        obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')


    if obj.soc_cut_type in ['Cutout']:
        obj.display_type = 'WIRE'
        for perimeter in find_siblings_by_type(obj, ['Perimeter']):
            setup(perimeter)  # need to rebuild the boolean modifiers

    if obj.soc_cut_type == 'Perimeter':
        for cut in find_siblings_by_type(obj, ['Cutout']):
            modifier_name = "SOC_Boolean." + cut.name
            bool = obj.modifiers.new(modifier_name, 'BOOLEAN')
            bool.operation = 'DIFFERENCE'
            bool.object = cut

    update(obj)


def update(obj):

    cut_type = obj.soc_cut_type

    if cut_type == 'Perimeter':
        if obj.soc_cut_depth < 0.0:
            obj.soc_cut_depth = 0.0

    elif cut_type == 'Cutout':
        obj.soc_cut_depth = perimeter_thickness(obj) + 0.2    # adding margin for boolean modifier

    if 'SOC_Solidify' in obj.modifiers:
        obj.modifiers['SOC_Solidify'].thickness = obj.soc_cut_depth


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
        return 10.0 # TODO unit





