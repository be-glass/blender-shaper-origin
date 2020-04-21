import datetime

import bpy

from . import generator
from .constant import DEFAULTS
from .preview import Preview
from .helper.other import check_duplication, length, store_selection, restore_selection


def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(post_ob_updated)


def unregister():
    bpy.app.handlers.depsgraph_update_post.clear()


@bpy.app.handlers.persistent
def post_ob_updated(scene, depsgraph):
    obj, selection = store_selection()
    # restore_selection(obj, selection)

    if obj is not None:
        if obj.mode == 'OBJECT':
            if obj.soc_object_type != 'None':
                check_duplication(obj)

                for o in selection:
                    handle_object_types(o, depsgraph)

    restore_selection(obj, selection)


def handle_object_types(obj, depsgraph):
    if obj.soc_object_type == 'Cut':
        for u in depsgraph.updates:
            if u.is_updated_geometry:
                generator.update(bpy.context, obj, reset=True)
            elif u.is_updated_transform:
                generator.transform(bpy.context, obj)
            else:
                generator.update_hide_state(bpy.context, obj)

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
            generator.update(context, obj)


def update_tool_diameter(obj, context):
    minimum, maximum = minmax(context, 'tool_diameter')

    if obj.soc_initialized:
        if obj.soc_tool_diameter < minimum:
            obj.soc_tool_diameter = minimum
        elif obj.soc_tool_diameter > maximum:
            obj.soc_tool_diameter = maximum
        else:
            generator.update(context, obj, reset=True)


def initialize_object(obj, context):
    obj.soc_cut_depth = default(context, 'cut_depth')
    obj.soc_tool_diameter = default(context, 'tool_diameter')
    obj.soc_initialized = True


def update_cut_type(obj, context):
    if not obj.soc_initialized:
        initialize_object(obj, context)
    generator.update(context, obj, reset=True)


def preview(scene_properties, context):
    if scene_properties.preview:
        Preview(context).create()
        pass
    else:
        Preview(context).delete()
