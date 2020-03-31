import bpy
from . import constants



def create_materials(context):

    # syntaxerror

    materials = bpy.data.materials
    for type, color in constants.cut_face_color.items():
        id = constants.prefix + type
        if id in materials.keys():
            m = materials[id]
        else:
            m = materials.new(id)
        m.diffuse_color = color
