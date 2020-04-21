import mathutils
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from mathutils.geometry import distance_point_to_plane

from .__init__ import bl_info
from .helper.op_export_svg import svg_content
from .helper.other import project_name, write, translate_local
from .helper.gen_helper import find_perimeters


def operators():
    return (
        MESH_OT_socut_export_cuts,
        MESH_OT_socut_align_object,
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
            name = project_name()
            selection_set = {name: items}

        for name, selection in selection_set.items():
            content = svg_content(context, selection, bl_info)
            file_name = f'{dir_name}/{name}.svg'
            write(content, file_name)

        self.report({'INFO'}, "OK")
        return {'FINISHED'}

class MESH_OT_socut_align_object(Operator):
    bl_idname = "mesh.socut_align_object"
    bl_label = "Align with Perimeter"
    bl_description = "Align a cut with the perimeter"

    def execute(self, context):

        obj = context.object
        collection = obj.users_collection[0]
        perimeters = find_perimeters(collection)

        if not perimeters:
            self.report({'ERROR'}, "No perimeter found.")
            return {'CANCELLED'}

        obj.matrix_world = perimeters[0].matrix_world
        d = distance_point_to_plane(obj.location, perimeters[0].location, perimeters[0].data.polygons[0].normal)

        translate_local(obj, mathutils.Vector((0, 0, d + .001)))

        self.report({'INFO'}, "OK")
        return {'FINISHED'}

