import bpy

from .lib.generator import Generator
from .lib.constant import DEFAULTS
from .lib.preview import Preview
from .lib.helper.other import consistency_checks, length, store_selection, restore_selection


def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(post_ob_updated)


def unregister():
    bpy.app.handlers.depsgraph_update_post.clear()


@bpy.app.handlers.persistent
def post_ob_updated(scene, depsgraph):
    obj, selection = store_selection(bpy.context, reset=True)

    if obj is not None:
        if obj.mode == 'OBJECT':
            if obj.soc_object_type != 'None':
                consistency_checks(obj)

                for o in selection:
                    handle_object_types(o, depsgraph)

    restore_selection(obj, selection)


def handle_object_types(obj, depsgraph):
    context = bpy.context
    if obj.soc_object_type == 'Cut':
        for u in depsgraph.updates:
            if u.is_updated_geometry:
                Generator(context).create(obj).reset()
            elif u.is_updated_transform:
                Generator(context).create(obj).transform()
            else:
                Generator(context).create(obj).update_hide_state()

    elif obj.soc_object_type == 'Preview':
        for u in depsgraph.updates:
            if u.is_updated_transform:
                if obj.soc_mesh_cut_type == 'Perimeter':
                    preview = Preview(bpy.context)
                    preview.transform_reference(obj)
                    preview.transform_siblings(obj)
                    preview.update_bounding_frame()

    elif obj.soc_object_type == 'Bounding':
        for u in depsgraph.updates:
            if u.is_updated_transform:
                Preview(bpy.context).transform_previews(bpy.context, obj)

    else:
        pass


# Update handlers

def minmax(context, property_name):
    d0, dd, d1 = DEFAULTS[property_name]
    return length(context, d0), \
           length(context, d1)


def default(context, property_name):
    d0, dd, d1 = DEFAULTS[property_name]
    return length(context, dd)


def update_cut_depth(obj, context):
    minimum, maximum = minmax(context, 'cut_depth')

    if obj.soc_initialized:
        if obj.soc_cut_depth < minimum:
            obj.soc_cut_depth = minimum
        elif obj.soc_cut_depth > maximum:
            obj.soc_cut_depth = maximum
        else:
            Generator(context).create(obj).update()


def update_tool_diameter(obj, context):
    minimum, maximum = minmax(context, 'tool_diameter')

    if obj.soc_initialized:
        if obj.soc_tool_diameter < minimum:
            obj.soc_tool_diameter = minimum
        elif obj.soc_tool_diameter > maximum:
            obj.soc_tool_diameter = maximum
        else:
            Generator(context).create(obj).reset()


def initialize_object(obj, context):
    obj.soc_cut_depth = default(context, 'cut_depth')
    obj.soc_tool_diameter = default(context, 'tool_diameter')
    obj.soc_initialized = True


def update_cut_type(obj, context):
    _, selection = store_selection(context, reset=True)
    if not obj.soc_initialized:
        initialize_object(obj, context)

    g = Generator(context)
    c = g.create(obj)
    c.reset()

    # Generator(context).create(obj).reset()
    restore_selection(obj, selection)


def preview(scene_properties, context):
    if scene_properties.preview:
        Preview(context).create()
        pass
    else:
        Preview(context).delete()
