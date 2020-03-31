import bpy
from . import constant


def create_materials(context):
    materials = bpy.data.materials
    for type, color in constant.cut_face_color.items():
        id = constant.prefix + type
        if id in materials.keys():
            m = materials[id]
        else:
            m = materials.new(id)
        m.diffuse_color = color


def create_sheet(context):
    if not constant.sheet_name in bpy.data.objects.keys():
        bpy.ops.mesh.primitive_plane_add(size=20.0)
        sheet = bpy.context.active_object
        sheet.name = constant.sheet_name
        sheet.data.polygons[0].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set(mode='OBJECT')