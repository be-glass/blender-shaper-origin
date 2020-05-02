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
from mathutils import Matrix

from .collection import Collection, Collect
from .object_types.bounding import Bounding
from .object_types.reference import Reference


class ProjectPreview:
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
                        add_object(self.cut_obj, self.collection, self.bounding, perimeter, obj)

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

    ABC

    def matrix_ref_bound(self, perimeter_mw, bounding_mw):

        reference_mw = Reference(perimeter)

        m3 = reference.matrix_world if reference else Matrix()
        m4 = bounding_mw if bounding_mw else Matrix()

        return m4 @ m3
