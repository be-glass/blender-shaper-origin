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
from typing import List

from bpy.types import Object, BlendDataObjects


class Project:

    @classmethod
    def name(self) -> str:
        name = (bpy.path.display_name_from_filepath(bpy.data.filepath))
        return name if name else "untitled"

    @classmethod
    def cut_objs(self) -> List[BlendDataObjects]:
        return [o for o in bpy.data.objects if o.soc_object_type == 'Cut']

    @classmethod
    def perimeter_objs(self) -> List[BlendDataObjects]:
        per_objs = [o for o in self.cut_objs() if o.soc_mesh_cut_type == 'Perimeter']
        return per_objs
