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

from .generators.bounding import Bounding
from .generators.curve_cut import CurveCut
from .generators.disabled import Disabled
from .generators.gen_preview import PreviewPerimeter
from .generators.mesh_cut import MeshCut
from .generators.mesh_guide import MeshGuide
from .generators.perimeter import Perimeter
from lib.object_types.shape.proxy import Proxy
from .generators.ignore import Ignore
from .helper.other import err_implementation


def create_cut(context, obj):
    ot = obj.soc_object_type

    if not obj.soc_simulate:
        cut = Disabled


    elif ot == 'Preview':
        if obj.soc_mesh_cut_type == 'Perimeter':
            cut = PreviewPerimeter
        elif obj.soc_mesh_cut_type != 'None':
            cut = Ignore
        elif obj.soc_curve_cut_type != 'None':
            cut = Ignore
        else:
            err_implementation(context)
            cut = Ignore

    elif ot == 'Bounding':
        cut = Bounding

    elif ot == 'Solid':
        cut = Ignore

    elif ot == 'Proxy':
        cut = Proxy
    else:
        cut = Disabled
    return cut(context, obj)
