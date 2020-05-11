#   This file is part of Blender_Shaper_Origin.
#  #
#   Blender_Shaper_Origin is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#  #
#   Blender_Shaper_Origin is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#  #
#   You should have received a copy of the GNU General Public License
#   along with Blender_Shaper_Origin.  If not, see <https://www.gnu.org/licenses/>.
#

import bpy
from bpy.types import Object, BlendDataObjects
from mathutils import Matrix

from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..helper.other import align_to_face


class Reference:

    def __init__(self, perimeter) -> None:
        self.cut_obj = perimeter.obj

    def get(self) -> BlendDataObjects:
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return self.create()

    @property
    def name(self) -> str:
        if not self.cut_obj.soc_reference_name:
            self.cut_obj.soc_reference_name = PREFIX + self.cut_obj.users_collection[0].name + '.reference'
        return self.cut_obj.soc_reference_name

    def matrix(self) -> Matrix:
        return self.get().matrix_world.copy()

    # private

    def create(self) -> Object:

        compartment = Compartment.by_enum(Collect.Reference)

        ref_obj = bpy.data.objects.new(self.name, None)
        ref_obj.location = self.cut_obj.location

        ref_obj.matrix_world = align_to_face(self.cut_obj.data.polygons[0]).inverted()

        compartment.link_obj(ref_obj)
        ref_obj.empty_display_size = 5
        ref_obj.empty_display_type = 'PLAIN_AXES'
        ref_obj.soc_object_type = 'Reference'
        ref_obj.name = self.name
        ref_obj.hide_set(True)
        return ref_obj
