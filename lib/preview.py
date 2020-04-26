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
from mathutils import Matrix, Vector

from .constant import FACE_COLOR
from .fillet import Fillet
from .helper.gen_helper import get_reference, boundaries
from .helper.preview_helper import transform_preview, get_bounding_frame, BOUNDING_FRAME_NAME
from .helper.mesh import create_object
from .helper.other import length, get_preview_collection, find_cuts, get_soc_collection, warning_msg, get_object_safely, \
    err_implementation


class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.bounding = get_bounding_frame()
        self.cut_objs = find_cuts()
        self.perimeters = [o for o in self.cut_objs if o.soc_mesh_cut_type == 'Perimeter']

    def create(self):
        if self.perimeters:
            self.bounding = self.update_bounding_frame()

            for perimeter in self.perimeters:
                for obj in perimeter.users_collection[0].objects:
                    if obj.soc_object_type == 'Cut':
                        self.add_object(perimeter, obj)

            self.set_viewport()
        else:
            self.bounding = None

    def set_viewport(self):
        for area in self.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'SOLID'
                        space.shading.color_type = 'OBJECT'

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)
        self.hide_bounding_frame()

    def hide_bounding_frame(self):
        frame = get_bounding_frame()
        if frame:
            frame.hide_set(True)

    def update_bounding_frame(self):
        frame = get_bounding_frame()
        if frame:
            mw = frame.matrix_world.copy()
            bpy.data.objects.remove(frame)
        else:
            mw = Matrix()

        c0, c1 = boundaries(self.context)

        z = -0.1
        d = length(self.context, '10mm')  # margin of preview sheet

        m0 = Vector([c1.x + d, c0.y - d, z])
        m1 = Vector([c1.x + d, c1.y + d, z])
        m2 = Vector([c0.x - d, c1.y + d, z])
        m3 = Vector([c0.x - d, c0.y - d, z])

        quad = [m0, m1, m2, m3]

        collection = get_soc_collection(self.context)
        frame = create_object(quad, collection, BOUNDING_FRAME_NAME)
        frame.matrix_world = mw
        frame.soc_object_type = "Bounding"
        return frame

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
            fillet = Fillet(self.context, cut_obj)
            preview_obj = fillet.create(reset=False, rounded=False, outside=is_perimeter)

        else:
            preview_obj = cut_obj.copy()
            preview_obj.data = cut_obj.data.copy()
            preview_obj.soc_curve_cut_type = cut_obj.soc_curve_cut_type

        self.collection.objects.link(preview_obj)
        if cut_obj.soc_mesh_cut_type != 'Perimeter':
            preview_obj.hide_select = True

        # apply_mesh_scale(self.context, preview_obj)    # TODO: is this needed? for mesh? for curve?

        preview_obj.matrix_world = transform_preview(self.context, cut_obj, perimeter, self.bounding)
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

            reference_obj = get_reference(self.context, obj)

            if reference_obj is not None:
                frame_1 = self.bounding.matrix_world.copy()
                frame_1.invert()
                # frame_1 = self.bounding.matrix_world.inverted()

                reference_obj.matrix_world = frame_1 @ preview_obj.matrix_world
                reference_obj.location.z = 0

    def transform_siblings(self, perimeter_preview):

        perimeters = [o for o in bpy.data.objects if o.soc_preview_name == perimeter_preview.name]
        if not perimeters:
            return
        perimeter = perimeters[0]

        for obj in perimeter.users_collection[0].objects:
            if obj.soc_mesh_cut_type != 'Perimeter':
                m = transform_preview(self.context, obj, perimeter, self.bounding)
                preview_obj = get_object_safely(obj.soc_preview_name)
                preview_obj.matrix_world = m

    def transform_previews(self, context, frame_obj):

        for perimeter in self.perimeters:
            for obj in perimeter.users_collection[0].objects:

                if obj.soc_object_type == 'Cut':
                    matrix = transform_preview(context, obj, perimeter, frame_obj)
                    preview_obj = get_object_safely(obj.soc_preview_name)
                    preview_obj.matrix_world = matrix
