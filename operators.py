from bpy import utils
from bpy.types import Operator
from bpy.utils import register_class, unregister_class


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


class MESH_OT_socut_export_cuts(Operator):
    bl_idname = "mesh.socut_export_cuts"
    bl_label = "SO Cuts Export"
    bl_description = "Export shapes to SVG for cutting with SO"

    def execute(self, context):
        print("export")
        return {'FINISHED'}

class MESH_OT_socut_create_materials(Operator):
    bl_idname = "mesh.socut_create_materials"
    bl_label = "SO Cuts Export"
    bl_description = "Create Materials to highlight cutting shapes"

    def execute(self, context):
        print("materials")
        return {'FINISHED'}

class MESH_OT_socut_create_sheet(Operator):
    bl_idname = "mesh.socut_create_sheet"
    bl_label = "SO Cuts Export"
    bl_description = "Create sheet to define dimensions and orientation of output."

    def execute(self, context):
        print("sheet")
        return {'FINISHED'}

