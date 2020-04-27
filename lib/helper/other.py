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
import itertools

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


def select_active(context, obj):
    for o in context.selected_objects:
        o.select_set(False)

    obj.select_set(True)
    context.view_layer.objects.active = obj


def error_msg(message, context=bpy.context):
    def msg(self, text):
        self.layout.label(text=message)

    context.window_manager.popup_menu(msg, title="Error", icon='ERROR')
    raise Exception(message)


def warning_msg(message, context=bpy.context):
    def msg(self, text):
        self.layout.label(text=message)

    context.window_manager.popup_menu(msg, title="Warning", icon='ERROR')
    # raise Exception(message)


def err_implementation(context=bpy.context):
    error_msg("missing implementation", context)


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


def length(context, quantity_with_unit):
    return bpy.utils.units.to_value('METRIC', 'LENGTH', quantity_with_unit) / context.scene.unit_settings.scale_length


def translate_local(obj, vector):
    rotation = obj.rotation_euler.to_matrix()
    rotation.invert()
    global_translation = vector @ rotation
    obj.location += global_translation


def get_collection(name, parent):
    if name in bpy.data.collections.keys():
        return bpy.data.collections[name]
    else:
        collection = bpy.data.collections.new(name)
        parent.children.link(collection)
        return collection


def get_soc_collection(context):
    return get_collection(PREFIX + "Internal", context.scene.collection)


def get_preview_collection(context):
    soc = get_soc_collection(context)
    return get_collection(PREFIX + "Preview", soc)


def get_solid_collection(context):
    soc = get_soc_collection(context)
    return get_collection(PREFIX + "Solid", soc)


def get_reference_collection(context):
    soc = get_soc_collection(context)
    collection = get_collection(PREFIX + "Reference", soc)
    return collection


def get_helper_collection(context):
    soc = get_soc_collection(context)
    collection = get_collection(PREFIX + "Helper", soc)
    return collection


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


def store_selection(context, reset=False):
    active_object = context.object
    selected_objects = context.selected_objects
    context.view_layer.objects.active = None
    if reset:
        for o in bpy.context.selected_objects:
            o.select_set(False)
    return active_object, selected_objects


def restore_selection(active_object, selected_objects):
    bpy.context.view_layer.objects.active = active_object
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in selected_objects:
        o.select_set(True)


def vector2string(vector):
    return SVG_COORD_FORMAT.format(vector[0], vector[1])


def minmax(context, property_name):
    d0, dd, d1 = DEFAULTS[property_name]
    return length(context, d0), \
           length(context, d1)


def default(context, property_name):
    d0, dd, d1 = DEFAULTS[property_name]
    return length(context, dd)


def initialize_object(obj, context):
    obj.soc_cut_depth = default(context, 'cut_depth')
    obj.soc_tool_diameter = default(context, 'tool_diameter')
    obj.soc_initialized = True
