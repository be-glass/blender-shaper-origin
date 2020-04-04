import bpy

from . import constant, helper


def delete_old_modifiers(obj):
    for modifier in obj.modifiers:
        if modifier.name.startswith(constant.prefix):
            obj.modifiers.remove(modifier)


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


def setup(context, obj):
    obj.display_type = 'TEXTURED'
    delete_old_modifiers(obj)
    delete_old_internals(obj)
    reset_curve(obj)

    internal_collection = get_internal_collection(constant.prefix + 'internal', obj)

    if not obj.soc_simulate:
        return

    if obj.soc_cut_type in ['Perimeter', 'Cutout', 'Pocket']:
        obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')

    if obj.soc_cut_type == 'Perimeter':
        for cut in find_siblings_by_type(obj, ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']):
            modifier_name = "SOC_Boolean." + cut.name
            boolean = obj.modifiers.new(modifier_name, 'BOOLEAN')
            boolean.operation = 'DIFFERENCE'

            if cut.soc_cut_type in ['Cutout', 'Pocket']:
                boolean.object = cut

            elif cut.soc_cut_type in ['Exterior', 'Interior', 'Online']:
                mesh_name = f'SOC_{cut.name}.mesh'
                boolean.object = helper.get_object_safely(mesh_name)
            else:
                helper.err_implementation()

    if obj.soc_cut_type in ['Exterior', 'Interior', 'Online']:
        if obj.type == 'CURVE':
            bevel = create_bevel_object(obj)
            helper.move_object(bevel, internal_collection)
            obj.data.bevel_object = bevel
            update_mesh(context, obj)

    if obj.soc_cut_type in ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']:
        obj.display_type = 'WIRE'
        for perimeter in find_siblings_by_type(obj, ['Perimeter']):
            setup(context, perimeter)  # need to rebuild the boolean modifiers

    update(context, obj)


def update_mesh(context, obj):
    mesh_name = constant.prefix + obj.name + '.mesh'
    helper.delete_object(mesh_name)

    internal_collection = get_internal_collection(constant.prefix + 'internal', obj)

    helper.select_active(context, obj)
    r = bpy.ops.object.convert(target='MESH', keep_original=True)
    bpy.ops.object.shade_flat()
    mesh = context.object
    mesh.name = mesh_name
    helper.move_object(mesh, internal_collection)
    helper.select_active(context, obj)

    reset_boolean_reference(obj, mesh)


def reset_boolean_reference(obj, target):
    perimeters = find_siblings_by_type(obj, 'Perimeter')

    modifier_name = f'SOC_Boolean.{obj.name}'

    for perimeter in perimeters:
        perimeter.modifiers[modifier_name].object = target


def reset_curve(obj):
    if obj.type == 'CURVE':
        obj.data.bevel_object = None


def delete_old_internals(obj):
    name = f'SOC_{obj.name}.bevel'

    # delete old object
    collection = obj.users_collection[0]
    if 'SOC_internal' in collection.children.keys():
        internal_collection = collection.children['SOC_internal']
        [bpy.data.objects.remove(o, do_unlink=True) for o in internal_collection.objects if
         o.name.startswith("SOC_" + obj.name)]


def create_bevel_object(obj):
    name = f'SOC_{obj.name}.bevel'

    # create new one
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    bevel = bpy.context.active_object
    bevel.name = name

    # move object origin to upper edge
    bevel.location = (0, -0.5, 0)
    bpy.ops.object.transform_apply()

    # scale
    bevel.scale = (obj.soc_tool_diameter, obj.soc_cut_depth, 1)

    # delete first face
    bpy.ops.object.mode_set(mode='EDIT')
    bevel.data.polygons[0].select = True
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.convert(target='CURVE')

    return bevel


def update(context, obj):
    cut_type = obj.soc_cut_type

    delta = 0.0  # margin for boolean modifier. TODO fix units

    if cut_type == 'Perimeter':
        if obj.soc_cut_depth < 0.0:
            obj.soc_cut_depth = 0.0
    elif cut_type == 'Cutout':
        obj.soc_cut_depth = perimeter_thickness(obj)
        delta = 0.2
    elif cut_type == 'Pocket':
        delta = 0.1

    if 'SOC_Solidify' in obj.modifiers:
        obj.modifiers['SOC_Solidify'].thickness = obj.soc_cut_depth + delta

    elif cut_type in ['Exterior', 'Interior', 'Online']:
        bevel = helper.get_object_safely(f'SOC_{obj.name}.bevel')
        bevel.scale = (obj.soc_tool_diameter, obj.soc_cut_depth, 1)
        update_mesh(context, obj)


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
