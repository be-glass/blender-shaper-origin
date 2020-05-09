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
from typing import List, Tuple

from bpy.types import Object

from ..constant import SVG_COORD_FORMAT, DEFAULTS, STACK_Z, SO_CUT_ENCODING


def write(content, file_name) -> str:
    try:
        with open(file_name, 'w') as file:
            file.writelines(content)
    except IOError as err:
        return str(err)

    return False  # no error


def select_active(obj) -> None:
    context = bpy.context
    for o in context.selected_objects:
        o.select_set(False)

    obj.select_set(True)
    context.view_layer.objects.active = obj


def error_msg(message) -> None:
    context = bpy.context

    def msg(self, text):
        self.layout.label(text=message)

    context.window_manager.popup_menu(msg, title="Error", icon='ERROR')
    raise Exception(message)


def warning_msg(message) -> None:
    def msg(self, text):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(msg, title="Warning", icon='ERROR')
    # raise Exception(message)


def get_object_safely(obj_name, report_error=True) -> Object:
    if obj_name in bpy.data.objects.keys():
        return bpy.data.objects[obj_name]
    elif report_error:
        error_msg(f'Cannot find (internal) object: "{obj_name}"')
    return None


def delete_object(obj_name) -> None:
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        bpy.data.objects.remove(obj, do_unlink=True)


def remove_object(name) -> None:
    if name in bpy.data.objects.keys():
        bpy.data.objects.remove(bpy.data.objects[name])


def hide_objects(name) -> None:
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.hide_set(True)


def length(quantity_with_unit) -> float:
    return bpy.utils.units.to_value('METRIC', 'LENGTH',
                                    quantity_with_unit) / bpy.context.scene.unit_settings.scale_length


def translate_local(obj, vector) -> None:
    rotation = obj.rotation_euler.to_matrix()
    rotation.invert()
    global_translation = vector @ rotation
    obj.location += global_translation


def consistency_checks(obj) -> None:
    if obj.soc_object_type is None:
        obj.soc_object_type = 'None'
    elif obj.soc_object_type == 'Cut':
        check_duplication(obj)
        check_state(obj)
        check_open_curves(obj)


def check_open_curves(obj) -> None:
    if obj.soc_curve_cut_type in ['Exterior', 'Interior']:
        if not obj.data.splines[0].use_cyclic_u:
            obj.soc_curve_cut_type = 'Online'


def check_state(obj) -> None:
    if obj.soc_mesh_cut_type == 'None' and obj.soc_curve_cut_type == 'None':
        reset_obj(obj)


def reset_obj(obj) -> None:
    obj.soc_object_type = 'None'
    obj.soc_mesh_cut_type = 'None'
    obj.soc_curve_cut_type = 'None'
    reset_relations(obj)


def reset_relations(obj) -> None:
    obj.soc_reference_name = ""
    obj.soc_preview_name = ""
    obj.soc_solid_name = ""
    obj.soc_bevel_name = ""
    obj.soc_known_as = ""


def check_duplication(obj) -> None:
    if not obj.soc_known_as:
        obj.soc_known_as = obj.name
    else:
        if obj.soc_known_as != obj.name:
            reset_obj(obj)

            # TODO: handle object renaming:
            # if obj.soc_known_as in bpy.data.objects.keys():
            #     reset_obj(obj)
            # else:  # obj appears to be renamed
            #     obj.soc_known_as = obj.name


def find_first_perimeter(obj) -> List[Object]:
    perimeters = [o for o in obj.users_collection[0].objects if o.soc_mesh_cut_type == 'Perimeter']
    if perimeters:
        return perimeters[0]
    else:
        return []


def store_selection(reset=False) -> Tuple[Object, List[Object]]:
    context = bpy.context
    active_object = context.object
    selected_objects = context.selected_objects
    context.view_layer.objects.active = None
    if reset:
        for o in context.selected_objects:
            o.select_set(False)
    return active_object, selected_objects


def restore_selection(active_object, selected_objects) -> None:
    c = bpy.context
    c.view_layer.objects.active = active_object
    for o in c.selected_objects:
        o.select_set(False)
    for o in selected_objects:
        o.select_set(True)


def vector2string(vector) -> str:
    return SVG_COORD_FORMAT.format(vector[0], vector[1])


def minmax(property_name) -> Tuple[float, float]:
    d0, dd, d1 = DEFAULTS[property_name]
    return length(d0), \
           length(d1)


def default(property_name) -> float:
    d0, dd, d1 = DEFAULTS[property_name]
    return length(dd)


def initialize_object(obj) -> None:
    obj.soc_cut_depth = default('cut_depth')
    obj.soc_tool_diameter = default('tool_diameter')
    obj.soc_initialized = True


def active_object() -> None:
    bpy.context.object


def set_viewport() -> None:
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'SOLID'
                    space.shading.color_type = 'OBJECT'


def z_lift(obj) -> float:
    if obj.soc_mesh_cut_type != 'None':
        z = STACK_Z[obj.soc_mesh_cut_type]
    elif obj.soc_curve_cut_type != 'None':
        z = STACK_Z[obj.soc_curve_cut_type]
    else:
        z = 0
    return z


def svg_material_attributes(key) -> str:
    style_map = {
        'Exterior': 'Exterior',
        'Interior': 'Interior',
        'Online': 'Online',
        'Pocket': 'Pocket',
        'Cutout': 'Pocket',
        'Perimeter': 'Exterior',
        'GuideArea': 'Guide',
        'GuidePath': 'Guide',
    }

    style = style_map[key]
    (stroke, fill) = SO_CUT_ENCODING[style]
    return f'stroke="{stroke}" fill="{fill}"'

