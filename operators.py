import mathutils
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from mathutils.geometry import distance_point_to_plane

from .lib.export import Export
from .lib.generator import create_cut
from .lib.helper.gen_helper import find_perimeters
from .lib.helper.other import translate_local, find_cuts, store_selection, consistency_checks
from .lib.preview import Preview


def operators():
    return (
        MESH_OT_socut_export_cuts,
        MESH_OT_socut_align_object,
        MESH_OT_socut_rebuild,
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

        # try:
        result = Export(context).run()
        # except:
        #     self.report({'ERROR'}, "Export Failed")
        #     return {'CANCELLED'}

        if result:
            self.report({'INFO'}, result)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Export Failed")
            return {'CANCELLED'}


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


class MESH_OT_socut_rebuild(Operator):
    bl_idname = "mesh.socut_rebuild"
    bl_label = "Rebuild everything"
    bl_description = "Rebuild all objects"

    def execute(self, context):
        _, selection = store_selection(context)

        preview = context.scene.so_cut['preview']
        context.scene.so_cut['preview'] = False

        for obj in find_cuts():
            consistency_checks(obj)
            create_cut(context, obj).reset()

        if preview:
            Preview(context).create()
            context.scene.so_cut['preview'] = True

        self.report({'INFO'}, "OK")
        return {'FINISHED'}
