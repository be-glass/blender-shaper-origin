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

from ..constant import PREFIX, SVG_COORD_FORMAT, DEFAULTS


def write(content, file_name):
    try:
        with open(file_name, 'w') as file:
            file.writelines(content)
    except IOError as err:
        return str(err)

    return False  # no error


def project_name():
    name = (bpy.path.display_name_from_filepath(bpy.data.filepath))
    name = name if name else "untitled"
    return name


def filter_valid(object_list, valid_types):
    return [obj for obj in object_list if obj.type in valid_types]


def check_type(obj, valid_types):
    remain = filter_valid([obj], valid_types)
    return True if remain else False


def move_object(obj, collection):
    [c.objects.unlink(obj) for c in obj.users_collection]
    collection.objects.link(obj)


def select_active(obj):
    context = bpy.context
    for o in context.selected_objects:
        o.select_set(False)

    obj.select_set(True)
    context.view_layer.objects.active = obj


def error_msg(message):
    context = bpy.context

    def msg(self, text):
        self.layout.label(text=message)

    context.window_manager.popup_menu(msg, title="Error", icon='ERROR')
    raise Exception(message)


def warning_msg(message):
    def msg(self, text):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(msg, title="Warning", icon='ERROR')
    # raise Exception(message)


def err_implementation():
    error_msg("missing implementation")


def get_object_safely(obj_name, report_error=True):
    if obj_name in bpy.data.objects.keys():
        return bpy.data.objects[obj_name]
    elif report_error:
        error_msg(f'Cannot find (internal) object: "{obj_name}"')
    return None


def delete_object(obj_name):
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        bpy.data.objects.remove(obj, do_unlink=True)


def hide_objects(name):
    for obj in bpy.data.objects:
        if obj.name.startswith(name):
            obj.hide_set(True)


def length(quantity_with_unit):
    return bpy.utils.units.to_value('METRIC', 'LENGTH',
                                    quantity_with_unit) / bpy.context.scene.unit_settings.scale_length


def translate_local(obj, vector):
    rotation = obj.rotation_euler.to_matrix()
    rotation.invert()
    global_translation = vector @ rotation
    obj.location += global_translation


def consistency_checks(obj):
    if obj.soc_object_type is None:
        obj.soc_object_type = 'None'
    elif obj.soc_object_type == 'Cut':
        check_duplication(obj)
        check_state(obj)
        check_open_curves(obj)


def check_open_curves(obj):
    if obj.soc_curve_cut_type in ['Exterior', 'Interior']:
        if not obj.data.splines[0].use_cyclic_u:
            obj.soc_curve_cut_type = 'Online'


def check_state(obj):
    if obj.soc_mesh_cut_type == 'None' and obj.soc_curve_cut_type == 'None':
        reset_obj(obj)


def reset_obj(obj):
    obj.soc_object_type = 'None'
    obj.soc_mesh_cut_type = 'None'
    obj.soc_curve_cut_type = 'None'
    reset_relations(obj)


def reset_relations(obj):
    obj.soc_reference_name = ""
    obj.soc_preview_name = ""
    obj.soc_solid_name = ""
    obj.soc_bevel_name = ""
    obj.soc_known_as = ""


def check_duplication(obj):
    if not obj.soc_known_as:
        obj.soc_known_as = obj.name
    else:
        if obj.soc_known_as != obj.name:
            if obj.soc_known_as in bpy.data.objects.keys():
                reset_obj(obj)
            else:  # obj appears to be renamed
                obj.soc_known_as = obj.name


def find_cuts():
    return [o for o in bpy.data.objects if o.soc_object_type == 'Cut']


def find_first_perimeter(obj):
    perimeters = [o for o in obj.users_collection[0].objects if o.soc_mesh_cut_type == 'Perimeter']
    if perimeters:
        return perimeters[0]
    else:
        return None


def store_selection(reset=False):
    context = bpy.context
    active_object = context.object
    selected_objects = context.selected_objects
    context.view_layer.objects.active = None
    if reset:
        for o in context.selected_objects:
            o.select_set(False)
    return active_object, selected_objects


def restore_selection(active_object, selected_objects):
    c = bpy.context
    c.view_layer.objects.active = active_object
    for o in c.selected_objects:
        o.select_set(False)
    for o in selected_objects:
        o.select_set(True)


def vector2string(vector):
    return SVG_COORD_FORMAT.format(vector[0], vector[1])


def minmax(property_name):
    d0, dd, d1 = DEFAULTS[property_name]
    return length(d0), \
           length(d1)


def default(property_name):
    d0, dd, d1 = DEFAULTS[property_name]
    return length(dd)


def initialize_object(obj):
    obj.soc_cut_depth = default('cut_depth')
    obj.soc_tool_diameter = default('tool_diameter')
    obj.soc_initialized = True


def active_object():
    bpy.context.object


def remove_by_name(name):
    bpy.data.objects.remove(bpy.data.objects[name])
