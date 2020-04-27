#  This file is part of Blender_Shaper_Origin.
#
#  Blender_Shaper_Origin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Blender_Shaper_Origin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Blender_Shaper_Origin.  If not, see <https://www.gnu.org/licenses/>.

import bpy

from .lib.generator import create_cut
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

    if obj is None:
        return

    # # extinguish interrupt chain
    # if obj.soc_suppress_next_update:
    #     obj.soc_suppress_next_update = False
    #     return

    if obj.mode == 'OBJECT':
        consistency_checks(obj)
        for o in selection:
            cut = create_cut(bpy.context, o)
            for u in depsgraph.updates:
                if u.is_updated_geometry:

                    if not obj.soc_suppress_next_update:  # extinguish interrupt chain
                        cut.reset()

                elif u.is_updated_transform:
                    cut.transform()
                else:
                    cut.update_hide_state()
    restore_selection(obj, selection)

    obj.soc_suppress_next_update = False


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
            create_cut(context, obj).update()


def update_tool_diameter(obj, context):
    minimum, maximum = minmax(context, 'tool_diameter')

    if obj.soc_initialized:
        if obj.soc_tool_diameter < minimum:
            obj.soc_tool_diameter = minimum
        elif obj.soc_tool_diameter > maximum:
            obj.soc_tool_diameter = maximum
        else:
            create_cut(context, obj).reset()


def initialize_object(obj, context):
    obj.soc_cut_depth = default(context, 'cut_depth')
    obj.soc_tool_diameter = default(context, 'tool_diameter')
    obj.soc_initialized = True


def update_cut_type(obj, context):
    _, selection = store_selection(context, reset=True)
    if not obj.soc_initialized:
        initialize_object(obj, context)

    create_cut(context, obj).reset()

    restore_selection(obj, selection)


def preview(scene_properties, context):
    if scene_properties.preview:
        Preview(context).create()
        pass
    else:
        Preview(context).delete()
