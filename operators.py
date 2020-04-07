import bpy
from bpy.types import Operator
from bpy.utils import register_class, unregister_class

from . import helper, constant
from . import op_export_svg

bl_info = {
    "name": "n/a",
    "author": "n/a",
    "version": (0, 0, 0),
}  # to be filled by __init__


def operators():
    return (
        MESH_OT_socut_export_cuts,
    )


def register():
    for widget in operators():
        register_class(widget)


def unregister():
    for widget in operators():
        unregister_class(widget)


def list_export_items(context):
    if context.scene.so_cut.selected_only:
        items = context.selected_objects
    else:
        items = context.scene.objects
    return [o for o in items if (o.soc_mesh_cut_type != 'None' or o.soc_curve_cut_type != 'None')]

class MESH_OT_socut_export_cuts(Operator):
    bl_idname = "mesh.socut_export_cuts"
    bl_label = "SO Cuts Export"
    bl_description = "Export shapes to SVG for cutting with SO"

    def execute(self, context):
        dir_name = context.scene.so_cut.export_path
        items = list_export_items(context)

        if context.scene.so_cut.separate_files:
            selection_set = {}
            for obj in items:
                name = obj.name
                selection_set[obj.name] = [obj]
        else:
            name = helper.project_name()
            selection_set = {name: items}

        for name, selection in selection_set.items():
            content = op_export_svg.svg_content(context, selection, bl_info)
            file_name = f'{dir_name}/{name}.svg'
            helper.write(content, file_name)

        self.report({'INFO'}, "OK")
        return {'FINISHED'}
