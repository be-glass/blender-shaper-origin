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
from mathutils import Vector

from .collection import Collection, Collect
from .constant import FACE_COLOR
from .fillet import Fillet
from .helper.gen_helper import get_reference
from .helper.other import warning_msg, get_object_safely, move_object
from .helper.preview_helper import transform_preview
from .object_types.bounding import Bounding


class Preview:
    def __init__(self):
        self.collection = Collection.by_enum(Collect.Preview).get()
        self.bounding = Bounding()
        self.perimeters = self.collection.perimeter_objs()

    def create(self):
        if self.perimeters:
            self.bounding.reset()

            for perimeter in self.perimeters:
                for obj in perimeter.users_collection[0].objects:
                    if obj.soc_object_type == 'Cut':
                        self.add_object(perimeter, obj)

            self.set_viewport()
        else:
            self.bounding.hide()

    def set_viewport(self):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'OBJECT'

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)
        self.bounding.hide()


    def add_object(self, perimeter, cut_obj):

        if cut_obj.scale != Vector([1, 1, 1]):
            warning_msg(
                f'Please apply scale to object "{cut_obj.name}" to avoid unexpected results in preview and export!')

        if cut_obj.soc_preview_name:
            name = cut_obj.soc_preview_name
        else:
            name = cut_obj.name + '.preview'

        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name])

        if cut_obj.type == 'MESH':
            is_perimeter = True if cut_obj.soc_mesh_cut_type == 'Perimeter' else False
            fillet = Fillet(self.cut_obj)
            preview_obj = fillet.create(reset=False, rounded=False, outside=is_perimeter)

        else:
            preview_obj = cut_obj.copy()
            preview_obj.data = cut_obj.data.copy()
            preview_obj.soc_curve_cut_type = cut_obj.soc_curve_cut_type

        move_object(preview_obj, self.collection)
        if cut_obj.soc_mesh_cut_type != 'Perimeter':
            preview_obj.hide_select = True

        # apply_mesh_scale(self.preview_obj)    # TODO: is this needed? for mesh? for curve?

        preview_obj.matrix_world = transform_preview(self.cut_obj, perimeter, self.bounding.frame())
        preview_obj.name = name
        cut_obj.soc_preview_name = preview_obj.name
        preview_obj.soc_preview_name = ""
        preview_obj.soc_known_as = preview_obj.name
        preview_obj.soc_object_type = 'Preview'
        preview_obj.display_type = 'TEXTURED'

        if cut_obj.soc_mesh_cut_type != 'None':
            preview_obj.color = FACE_COLOR[cut_obj.soc_mesh_cut_type]
            preview_obj.soc_mesh_cut_type = cut_obj.soc_mesh_cut_type
        elif cut_obj.soc_curve_cut_type != 'None':
            preview_obj.color = FACE_COLOR[cut_obj.soc_curve_cut_type]
            preview_obj.soc_curve_cut_type = cut_obj.soc_curve_cut_type

        return preview_obj

    def transform_reference(self, preview_obj):
        matches = [o for o in bpy.data.objects if o.soc_preview_name == preview_obj.name]
        if matches:
            obj = matches[0]

            reference_obj = get_reference(self.obj)

            if reference_obj is not None:
                frame_1 = Bounding.matrix_inverted()

                reference_obj.matrix_world = frame_1 @ preview_obj.matrix_world
                reference_obj.location.z = 0

    def transform_siblings(self, perimeter_preview):

        perimeters = [o for o in bpy.data.objects if o.soc_preview_name == perimeter_preview.name]
        if not perimeters:
            return
        perimeter = perimeters[0]

        for obj in perimeter.users_collection[0].objects:
            if obj.soc_mesh_cut_type != 'Perimeter':
                m = transform_preview(self.obj, perimeter, self.bounding.matrix())
                preview_obj = get_object_safely(obj.soc_preview_name)
                preview_obj.matrix_world = m

