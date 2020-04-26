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

import math

from .base import Generator
from .proxy import Proxy
from ..fillet import Fillet
from ..helper.gen_helper import *
from ..helper.preview_helper import lift_z
from ..helper.svg import svg_material_attributes


class MeshCut(Generator):

    def setup(self):
        super().setup()
        self.obj.soc_object_type = 'Cut'

        self.fillet = Fillet(self.context, self.obj)
        self.fillet.create()
        self.fillet.display_type = 'WIRE'

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.get_fillet_obj()

        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection)

    def update(self):

        cut_type = self.obj.soc_mesh_cut_type

        if cut_type == 'Cutout':

            thickness = perimeter_thickness(self.obj)
            if thickness:
                cutout_depth = thickness + self.length('1mm')
            else:
                cutout_depth = self.length('1cm')

            if not math.isclose(self.obj.soc_cut_depth, cutout_depth, abs_tol=self.length('0.01mm')):
                self.obj.soc_cut_depth = cutout_depth
                return

            delta = 0.0
        elif cut_type == 'Pocket':
            delta = self.length('0.1mm')
        else:
            delta = 0.0

        self.adjust_solidify_thickness(delta=delta)

    def transform(self):
        fillet_obj = self.get_fillet_obj()
        fillet_obj.matrix_world = self.obj.matrix_world

    def svg(self):

        fillet = Fillet(self.context, self.obj)
        fillet_obj = fillet.create()
        proxy = Proxy(self.context, fillet_obj)
        proxy.setup_proxy(self.obj)

        content = proxy.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
        contents = self.svg_object(content, attributes)
        z = lift_z(self.context, self.obj)

        return z, contents
