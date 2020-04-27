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


class MeshGuide(Generator):

    def setup(self):
        super().setup()
        self.obj.soc_object_type = 'Cut'

    def update(self):
        pass

    def transform(self):
        pass

    def svg(self):
        content = self.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
        contents = self.svg_object(content, attributes)
        z = lift_z(self.context, self.obj)

        return z, contents
