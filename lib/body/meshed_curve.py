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

from .__init__ import Body
from ..helper.curve import face_is_down, curve2mesh
from ..helper.mesh_helper import shade_mesh_flat
from ..helper.other import remove_object, hide_objects, select_active


class MeshedCurve(Body):

    def setup(self) -> None:

        remove_object(self.name)
        self.shape.setup()

    def update(self) -> None:

        sign = int(face_is_down(self.cut_obj)) * 2 - 1

        for p in self.cut_obj.data.splines[0].points:
            p.radius = 1.0

        bevel = self.shape.get_bevel_object()
        bevel.scale = (sign * self.cut_obj.soc_tool_diameter, self.cut_obj.soc_cut_depth, 1)

        self.cut_obj.data.bevel_object = bevel

        if not self.cut_obj.data.splines[0].use_cyclic_u:
            self.cut_obj.data.use_fill_caps = True

        mesh = curve2mesh(self.cut_obj)
        self.cut_obj.data.bevel_object = None

        if self.name in bpy.data.objects.keys():
            self.obj = bpy.data.objects[self.name]
            self.obj.data = mesh
        else:
            self.obj = bpy.data.objects.new(self.name, mesh)  # !!!
            self.obj.matrix_world = self.cut_obj.matrix_world
            self.compartment.link(self.obj)

        remove_doubles(self.obj)

        self.obj.soc_solid_name = self.name
        self.obj.soc_object_type = 'Solid'

        shade_mesh_flat(self.obj)
        hide_objects(self.obj.name)

    def is_solid(self) -> bool:
        return not self.shape.is_guide()


def remove_doubles(obj) -> None:
    select_active(obj)
    obj.data.update()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.01)
    bpy.ops.object.mode_set(mode='OBJECT')
