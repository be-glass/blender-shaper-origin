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
from .__init__ import Shape
from .mesh_shape import MeshShape
from ..blender.project import Project


class Perimeter(MeshShape):

    @classmethod
    def all(cls):
        return [Perimeter(o) for o in Project.perimeter_objs()]

    def config(self):
        pass

    def setup(self):
        self.obj.display_type = 'WIRE'

    def update(self):
        pass

    def clean(self):
        pass

    def is_exterior(self):
        return True

    def is_perimeter(self):
        return True

    def shapes(self):
        objs = self.obj.users_collection[0].objects
        return [Shape.factory(o) for o in objs if o.soc_object_type == 'Cut']

    def others(self):
        return [o for o in self.shapes() if o.soc_mesh_cut_type != 'Perimeter']

    def preview_objs(self):
        objs = self.obj.users_collection[0].objects
        return [o for o in objs if o.soc_object_type == 'Cut']

    def matrix(self):
        return self.obj.matrix_world

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