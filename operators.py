import mathutils
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from mathutils.geometry import distance_point_to_plane

from .export import Export
from .helper.gen_helper import find_perimeters
from .helper.other import translate_local


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


class MESH_OT_socut_export_cuts(Operator):
    bl_idname = "mesh.socut_export_cuts"
    bl_label = "SO Cuts Export"
    bl_description = "Export shapes to SVG for cutting with SO"

    def execute(self, context):

        result = Export(context).run()

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
