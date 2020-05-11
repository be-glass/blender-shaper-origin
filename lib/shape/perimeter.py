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
from typing import TypeVar, List

from bpy.types import Object
from mathutils import Matrix

from .__init__ import Shape
from .mesh_shape import MeshShape
from ..blender.project import Project

T = TypeVar('T', bound='Perimeter')


class Perimeter(MeshShape):

    @classmethod
    def all(cls) -> List[T]:
        return [Perimeter(o) for o in Project.perimeter_objs()]

    def config(self) -> None:
        pass

    def setup(self) -> None:
        self.obj.display_type = 'WIRE'

    def update(self) -> None:
        pass

    def clean(self) -> None:
        pass

    def is_exterior(self) -> bool:
        return True

    def is_perimeter(self) -> bool:
        return True

    def shapes(self) -> List[T]:
        objs = self.obj.users_collection[0].objects
        return [Shape.factory(o) for o in objs if o.soc_object_type == 'Cut']

    def others(self) -> List[Object]:
        objs = self.obj.users_collection[0].objects
        return [o for o in objs if o.soc_mesh_cut_type != 'Perimeter']

    def sibling_objs(self) -> List[Object]:
        objs = self.obj.users_collection[0].objects
        return [o for o in objs if o.soc_object_type == 'Cut' and o is not self.obj]

    def objects(self) -> List[Object]:
        return [o for o in self.obj.users_collection[0].objects if o.soc_object_type != "None"]

    def matrix(self) -> Matrix:
        return self.obj.matrix_world

    def matrix_1(self) -> Matrix:
        return self.obj.matrix_world.inverted()

#
# class Perimeter(Generator):
#
#     def svg(self):
#         fillet = Fillet(self.self.obj)
#         fillet_obj = fillet.create(outside=True)
#         proxy = Proxy(self.fillet_obj)
#         proxy.setup_proxy(self.obj)
#
#         attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
#         content = proxy.svg_mesh()
#         z = lift_z(self.self.obj)
#         contents = self.svg_object(content, attributes)
#
#         return z, contents
#