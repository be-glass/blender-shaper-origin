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
from .mesh_shape import MeshShape


class Perimeter(MeshShape):

    def config(self):
        pass

    def setup(self):
        pass

    def update(self):
        pass

    def clean(self):
        pass

        ### private

    def is_exterior(self):
        return True

    def is_perimeter(self):
        return True

# from .fillet import Fillet
# from ..helper.gen_helper import *
# from ..helper.other import get_object_safely
# from ..helper.preview_helper import lift_z
# from ..helper.svg import svg_material_attributes
# from lib.object_types.preview import Preview
#
#
# class Perimeter(Generator):
#
#     def setup(self):
#         super().setup()
#
#         self.obj.soc_object_type = 'Cut'
#
#         self.fillet = Fillet(self.self.obj)
#         self.fillet.create(outside=True)
#         self.fillet.display_type = 'WIRE'
#
#
#         types = ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']
#         for cut_obj in find_siblings_by_type(types, sibling=self.obj):
#             self.rebuild_boolean_modifier(self.obj, cut_obj)
#
#         self.reference = get_reference(self.self.obj)
#
#         if self.context.scene.so_cut.preview:
#             Preview(self.context).add_object(self.obj, self.obj)
#
#     def update(self):
#
#         self.adjust_solidify_thickness()
#
#         cutouts = find_siblings_by_type('Cutout', sibling=self.context.object)
#         for cut in cutouts:
#             cut.soc_cut_depth = self.obj.soc_cut_depth + self.length('1mm')
#
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
#     def transform(self):
#         fillet_obj = self.get_fillet_obj()
#         fillet_obj.matrix_world = self.obj.matrix_world
