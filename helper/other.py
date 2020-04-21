import bpy
import itertools

from ..constant import PREFIX


def write(content, file_name):
    file = open(file_name, 'w')
    if file:
        if file.writelines(content):
            file.close()
            return True
        else:
            file.close()
    return False


def write_nested_list(nested_list, file_name):
    content = list(itertools.chain(*nested_list))
    return write(content, file_name)


def project_name():
    name = (bpy.path.display_name_from_filepath(bpy.data.filepath))
    name = name if name else "untitled"
    return name


def filter_valid(object_list, valid_types):
    return [obj for obj in object_list if obj.type in valid_types]


def check_type(obj, valid_types):
    remain = filter_valid([obj], valid_types)
    return True if remain else False


def add_Empty_at(*location):
    bpy.ops.object.add(type='EMPTY', location=(location))


def transform_if_needed(obj, coordinates):
    if obj.soc_reference_frame == 'local':
        return coordinates
    elif obj.soc_reference_frame == 'object':
        return 'TODO'  # a feature missing implementation. TODO will be printed into the SVG file
    else:  # 'global'
        return obj.matrix_world @ coordinates


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
    print("DEBUG me")


def warning_msg(message, context=bpy.context):
    def msg(self, text):
        self.layout.label(text=message)

    context.window_manager.popup_menu(msg, title="Warning", icon='ERROR')
    print("DEBUG me")


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


def get_collection(context, name, parent):
    if name in bpy.data.collections.keys():
        return bpy.data.collections[name]
    else:
        collection = bpy.data.collections.new(name)
        parent.children.link(collection)
        return collection


def get_soc_collection(context):
    return get_collection(context, "SOC", context.scene.collection)


def get_preview_collection(context):
    soc = get_soc_collection(context)
    return get_collection(context, PREFIX + "Preview", soc)


def get_solid_collection(context):
    soc = get_soc_collection(context)
    return get_collection(context, PREFIX + "Solid", soc)


def get_reference_collection(context):
    soc = get_soc_collection(context)
    collection = get_collection(context, PREFIX + "Reference", soc)
    return collection


def check_duplication(obj):
    if not obj.soc_known_as:
        obj.soc_known_as = obj.name
    else:
        if obj.soc_known_as != obj.name:
            if obj.soc_known_as in bpy.data.objects.keys():  # obj has been duplicated -> reset
                obj.soc_object_type = 'None'
                obj.soc_mesh_cut_type = 'None'
                obj.soc_curve_cut_type = 'None'
                obj.soc_reference_name = ""
                obj.soc_preview_name = ""
                obj.soc_solid_name = ""
                obj.soc_known_as = ""
            else:  # obj appears to be renamed
                obj.soc_known_as = obj.name


def find_cuts():
    return [o for o in bpy.data.objects if o.soc_object_type == 'Cut']


def find_perimeters(obj):
    return [o for o in obj.users_collection[0].objects if o.soc_mesh_cut_type == 'Perimeter']
