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

from ..helper.gen_helper import *
from ..helper.other import get_solid_collection, err_implementation

from .simulation import Simulation
from .reference import Reference
from .preview import Preview


class Cut:

    def __init__(self, context, obj):
        self.context = context
        self.obj = obj

        self.sim = Simulation(context, obj)
        self.preview = Preview(context, obj)

    def reset(self):
        # self.obj.soc_suppress_next_update = True
        self.cleanup()
        self.setup()
        self.update()

    def setup(self):
        self.sim.setup()
        self.preview.setup()

    def update(self):
        self.sim.update()
        self.preview.update()

    def cleanup(self):
        self.sim.cleanup()
        self.preview.cleanup()

    def svg(self):
        pass
