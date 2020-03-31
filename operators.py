import bpy
from bpy import utils
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from . import op_initialization, op_export_svg


bl_info = {
    "name": "n/a",
    "author": "n/a",
    "version": (0, 0, 0),
}   # to be filled by __init__

def operators():
    return (
        MESH_OT_socut_export_cuts,
        MESH_OT_socut_create_materials,
        MESH_OT_socut_create_sheet,
    )


def register():
    for widget in operators():
        register_class(widget)


def unregister():
    for widget in operators():
        unregister_class(widget)


class MESH_OT_socut_create_materials(Operator):
    bl_idname = "mesh.socut_create_materials"
    bl_label = "SO Cuts Export"
    bl_description = "Create Materials to highlight cutting shapes"

    def execute(self, context):

        op_initialization.create_materials(context)
        return {'FINISHED'}


class MESH_OT_socut_create_sheet(Operator):
    bl_idname = "mesh.socut_create_sheet"
    bl_label = "SO Cuts Export"
    bl_description = "Create sheet to define dimensions and orientation of output."

    def execute(self, context):
        op_initialization.create_sheet(context)
        return {'FINISHED'}


class MESH_OT_socut_export_cuts(Operator):
    bl_idname = "mesh.socut_export_cuts"
    bl_label = "SO Cuts Export"
    bl_description = "Export shapes to SVG for cutting with SO"

    def execute(self, context):

        content = op_export_svg.svg_header(bl_info) + \
                  op_export_svg.svg_body(context) + \
                  op_export_svg.svg_footer()

        dir_name = context.scene.so_cut.export_path
        file_name = context.active_object.name

        file = open( f'{dir_name}/{file_name}', 'w' )
        if file:
            file.write(content)
            file.close()

        return {'FINISHED'}




