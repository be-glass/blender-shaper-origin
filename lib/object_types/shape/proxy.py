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
from lib.helper.gen_helper import *
from lib.helper.other import find_first_perimeter


class Proxy(Generator):

    def setup_proxy(self, source_obj):
        self.perimeter = find_first_perimeter(source_obj)
        if self.perimeter:
            reference = get_reference(self.context, self.perimeter)
            self.obj.soc_reference_name = reference.name
        self.obj.soc_object_type = 'Proxy'
