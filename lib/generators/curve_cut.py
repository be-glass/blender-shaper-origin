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

from .base import Generator
from ..helper.curve import add_nurbs_square, face_is_down
from ..helper.gen_helper import *
from ..helper.mesh import repair_mesh, shade_mesh_flat, curve2mesh
from ..helper.other import get_solid_collection, get_object_safely, delete_object, hide_objects, get_helper_collection
from ..helper.preview_helper import lift_z
from ..helper.svg import svg_material_attributes
from .proxy import Proxy


class CurveCut(Generator):

    def svg(self):

        mesh_obj = curve2mesh(self.context, self.obj, add_face=True)
        proxy = Proxy(self.context, mesh_obj)
        proxy.setup_proxy(self.obj)

        content = proxy.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_curve_cut_type)
        z = lift_z(self.context, self.obj)

        return z, self.svg_object(content, attributes)

    def setup(self):
        super().setup()

        self.obj.soc_object_type = 'Cut'
        self.fillet = None
        self.obj.display_type = 'WIRE'

    def update(self):

        sign = int(face_is_down(self.context, self.obj)) * 2 - 1

        for p in self.obj.data.splines[0].points:
            p.radius = 1.0

        bevel = self.get_bevel_object()
        bevel.scale = (sign * self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)
        self.obj.data.bevel_object = bevel
        solid_obj = self.update_mesh()
        self.obj.data.bevel_object = None
        self.obj.soc_solid_name = solid_obj.name
        collections = self.obj.users_collection
        if collections:
            self.adjust_boolean_modifiers(collections[0])

    def get_bevel_object(self):
        if self.obj.soc_bevel_name:
            bevel_obj = get_object_safely(self.obj.soc_bevel_name, report_error=False)
            if bevel_obj:
                return bevel_obj

        collection = get_helper_collection(self.context)
        name = f'{PREFIX}{self.obj.name}.bevel'
        bevel_obj = add_nurbs_square(collection, name, self.obj.soc_curve_cut_type)
        bevel_obj.soc_object_type = 'Helper'
        bevel_obj.hide_set(True)
        self.obj.soc_bevel_name = bevel_obj.name

        return bevel_obj

    def update_mesh(self):
        mesh_name = PREFIX + self.obj.name + '.mesh'
        delete_object(mesh_name)

        cleanup_meshes(self.context, mesh_name)
        mesh_obj = curve2mesh(self.context, self.obj, mesh_name)
        get_solid_collection(self.context).objects.link(mesh_obj)

        shade_mesh_flat(mesh_obj)
        repair_mesh(self.context, mesh_obj)  # TODO: needed?
        hide_objects(mesh_obj.name)

        return mesh_obj

    def transform(self):
        solid_obj = get_object_safely(self.obj.soc_solid_name, report_error=False)
        if solid_obj:
            solid_obj.matrix_world = self.obj.matrix_world
