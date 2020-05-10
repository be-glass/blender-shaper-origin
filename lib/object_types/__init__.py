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

from typing import Union

from .bounding import Bounding
from .cut import Cut
from .inactive import Inactive
from .preview import Preview


def type_factory(obj) -> Union[None, Cut, Preview, Bounding, Inactive]:
    sot = obj.soc_object_type
    if sot in ['None', 'Cut']:
        item = Cut(obj)
    elif sot == 'Preview':
        item = Preview(obj)
    elif sot == 'Bounding':
        item = Bounding()
    else:
        item = Inactive()
    return item
