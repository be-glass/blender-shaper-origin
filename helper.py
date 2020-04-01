import bpy
import itertools


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



