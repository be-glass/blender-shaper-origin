#  This file is part of Blender_Shaper_Origin.
#
#  Blender_Shaper_Origin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Blender_Shaper_Origin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Blender_Shaper_Origin.  If not, see <https://www.gnu.org/licenses/>.
import bpy
import mathutils
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from mathutils.geometry import distance_point_to_plane

from .lib.blender.project import Project
from .lib.blender.collection import Collection
from .lib.object_types.cut import Cut
from .lib.export import Export
from .lib.helper.other import translate_local, store_selection, consistency_checks, reset_relations
from .lib.projectpreview import ProjectPreview

bl_info = None  # injected from init


def operators():
    return (
        MESH_OT_socut_export_cuts,
        MESH_OT_socut_align_object,
        MESH_OT_socut_rebuild,
    )


def register():
    for widget in operators():
        register_class(widget)

    bpy.utils.register_class(delete_override)


def unregister():
    for widget in operators():
        unregister_class(widget)

    bpy.utils.unregister_class(delete_override)


class MESH_OT_socut_export_cuts(Operator):
    bl_idname = "mesh.socut_export_cuts"
    bl_label = "SO Cuts Export"
    bl_description = "Export shapes to SVG for cutting with SO"

    def execute(self, context):

        result = Export().run()

        if result == False:
            self.report({'INFO'}, 'Export done')
            return {'FINISHED'}
        elif result:
            self.report({'WARNING'}, result)
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

        perimeters = Collection.by_obj(obj).perimeter_objs()

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
        _, selection = store_selection()

        preview = context.scene.so_cut.preview
        context.scene.so_cut['preview'] = False

        for obj in Project.cut_objs():
            reset_relations(obj)
            consistency_checks(obj)
            Cut(obj).reset()

        if preview:
            ProjectPreview().create()
            context.scene.so_cut['preview'] = True

        self.report({'INFO'}, "OK")
        return {'FINISHED'}


# delete override


class delete_override(bpy.types.Operator):
    """delete objects and their derivatives"""
    bl_idname = "object.delete"
    bl_label = "Object Delete Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        for obj in context.selected_objects:
            Cut(obj).clean()
            bpy.data.objects.remove(obj)
        return {'FINISHED'}
