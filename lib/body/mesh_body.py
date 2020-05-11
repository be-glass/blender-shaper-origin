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

from bpy.types import Object

from .__init__ import Body
from ..blender.compartment import Compartment
from ..blender.fillet import Fillet
from ..constant import ALIGNMENT_Z_OFFSET


class MeshBody(Body):

    def setup(self) -> None:
        self.shape.setup()

        if not self.shape.is_guide():
            self.obj = self.create_body_obj()
            self.compartment.collect(self.obj, self.name)

            if self.shape.is_perimeter():
                self.obj.display_type = 'TEXTURED'
            else:
                self.obj.display_type = 'WIRE'
                if Compartment.by_obj(self.cut_obj).perimeter_objs():
                    self.obj.hide_set(True)
                else:
                    self.obj.hide_set(False)
            self.obj.hide_select = True

    def update(self) -> None:
        self.shape.update()

    def is_solid(self) -> bool:
        return not self.shape.is_guide()

    # private

    def create_body_obj(self) -> Object:
        body = Fillet(self.shape.obj).create(self.shape.is_exterior(), rounded=True)
        body.matrix_world = self.cut_obj.matrix_world
        body.soc_object_type = 'Solid'
        return body

    def outside(self) -> bool:
        return self.shape.is_exterior()

    def thickness_delta(self) -> float:
        if self.cut_obj.soc_mesh_cut_type == 'Cutout':
            return ALIGNMENT_Z_OFFSET * 2
        else:
            return 0.0
