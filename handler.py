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

from .lib.preview import Preview
from .lib.helper.other import consistency_checks, store_selection, restore_selection, minmax, initialize_object
from .lib.object_types.cut import Cut
from .lib.object_types.inactive import Inactive


def register():
    bpy.app.handlers.depsgraph_update_post.clear()
    bpy.app.handlers.depsgraph_update_post.append(post_ob_updated)
    bpy.app.handlers.depsgraph_update_pre.append(pre_ob_updated)


def unregister():
    bpy.app.handlers.depsgraph_update_post.clear()


@bpy.app.handlers.persistent
def post_ob_updated(scene, depsgraph):
    obj, selection = store_selection(reset=True)

    if obj is None:
        return

    if obj.mode == 'OBJECT':
        consistency_checks(obj)
        for o in selection:
            cut = Cut(o)
            for u in depsgraph.updates:
                if u.is_updated_geometry:

                    if not obj.soc_suppress_next_update:  # extinguish interrupt chain
                        obj.soc_suppress_next_update = True
                        cut.reset()

                elif u.is_updated_transform:
                    cut.transform()
                else:
                    # cut.update_hide_state()   #TMP
                    pass

    restore_selection(obj, selection)
    obj.soc_suppress_next_update = False


# Update handlers


def update_cut_depth(obj, context):
    minimum, maximum = minmax('cut_depth')

    if obj.soc_initialized:
        if obj.soc_cut_depth < minimum:
            obj.soc_cut_depth = minimum
        elif obj.soc_cut_depth > maximum:
            obj.soc_cut_depth = maximum
        else:
            Cut(obj).update()


def update_tool_diameter(obj, context):
    minimum, maximum = minmax('tool_diameter')

    if obj.soc_initialized:
        if obj.soc_tool_diameter < minimum:
            obj.soc_tool_diameter = minimum
        elif obj.soc_tool_diameter > maximum:
            obj.soc_tool_diameter = maximum
        else:
            Cut(obj).reset()


def update_cut_type(obj, context):
    _, selection = store_selection(reset=True)
    if not obj.soc_initialized:
        initialize_object(obj)

    Cut(obj).reset()

    restore_selection(obj, selection)


def preview(scene_properties, context):
    if scene_properties.preview:
        Preview().create()
        pass
    else:
        Preview().delete()


def type_factory(obj):
    if obj.soc_object_type in ['None', 'Cut']:
        cls = Cut
    else:
        cls = Inactive
    return cls
