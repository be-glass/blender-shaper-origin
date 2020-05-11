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
from bpy.types import Operator
from bpy.utils import register_class, unregister_class
from mathutils import Matrix
from typing import List, Type, Set

from .lib.helper.other import align_to_face
from .lib.constant import ALIGNMENT_Z_OFFSET
from .lib.blender.compartment import Compartment, Collect
from .lib.blender.project import Project
from .lib.export import Export
from .lib.helper.curve import curve2mesh
from .lib.helper.mesh_helper import fill_polygon
from .lib.helper.other import store_selection, consistency_checks, reset_relations, \
    find_first_perimeter
from .lib.object_types.cut import Cut
from .lib.object_types.preview import Preview


def operators() -> List[Type[Operator]]:
    return [
        MESH_OT_socut_export_cuts,
        MESH_OT_socut_align_object,
        MESH_OT_socut_rebuild,
    ]


def register() -> None:
    for widget in operators():
        register_class(widget)

    bpy.utils.register_class(delete_override)


def unregister() -> None:
    for widget in operators():
        unregister_class(widget)

    bpy.utils.unregister_class(delete_override)


class MESH_OT_socut_export_cuts(Operator):
    bl_idname = "mesh.socut_export_cuts"
    bl_label = "SO Cuts Export"
    bl_description = "Export shapes to SVG for cutting with SO"

    def execute(self, context) -> Set[str]:

        result = Export(context).run()

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

    def execute(self, context) -> Set[str]:
        obj = context.object

        perimeter = find_first_perimeter(obj)

        if obj.type == 'CURVE':
            mesh = curve2mesh(obj)
            fill_polygon(mesh)
        else:  # obj.type == 'MESH':
            mesh = obj.data

        p_normal = perimeter.data.polygons[0].normal
        margin = Matrix.Translation(p_normal.normalized() * ALIGNMENT_Z_OFFSET)

        p_matrix = align_to_face(perimeter.data.polygons[0])
        o_matrix = align_to_face(mesh.polygons[0])

        obj.matrix_world = perimeter.matrix_world @ margin @ p_matrix @ o_matrix.inverted()

        self.report({'INFO'}, "OK")
        return {'FINISHED'}


class MESH_OT_socut_rebuild(Operator):
    bl_idname = "mesh.socut_rebuild"
    bl_label = "Rebuild everything"
    bl_description = "Rebuild all objects"

    def execute(self, context) -> Set[str]:
        _, selection = store_selection()

        Compartment.by_enum(Collect.Internal).delete_all()

        preview = context.scene.so_cut.preview
        context.scene.so_cut['preview'] = False

        for obj in Project.cut_objs():
            reset_relations(obj)
            consistency_checks(obj)
            Cut(obj).reset()

        if preview:
            Preview.create()
            context.scene.so_cut['preview'] = True

        self.report({'INFO'}, "OK")
        return {'FINISHED'}


# delete override


class delete_override(bpy.types.Operator):
    """delete objects and their derivatives"""
    bl_idname = "object.delete"
    bl_label = "Object Delete Operator"

    @classmethod
    def poll(cls, context) -> None:
        return context.active_object is not None

    def execute(self, context) -> Set[str]:
        for obj in context.selected_objects:
            if obj.soc_object_type == 'Cut':
                Cut(obj).clean()
            bpy.data.objects.remove(obj)
        return {'FINISHED'}
