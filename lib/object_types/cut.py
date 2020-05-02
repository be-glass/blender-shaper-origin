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
import bpy

from .solid import Solid


class Cut:

    def __init__(self, obj):
        self.obj = obj
        self.defaults()
        self.valid = self.check()

    def defaults(self):
        # self.obj.soc_object_type = 'None'
        self.solid = None
        self.preview = None

    def reset(self):
        self.clean()
        self.defaults()
        self.setup()
        self.update()

    def clean(self):
        Solid(self.obj).clean()
        # self.preview.cleanup()

    def setup(self):

        from .preview import Preview

        if not self.valid:
            return

        self.obj.soc_object_type = 'Cut'

        # Solid
        if self.obj.soc_simulate:
            self.solid = Solid(self.obj)
            self.solid.setup()

        # Preview
        if bpy.context.scene.so_cut.preview:
            self.preview = Preview.setup(self.obj)
            self.preview.config()
            self.preview.setup()


    def update(self):
        Solid(self.obj).update()
            # self.preview.update()
        pass

    def svg(self):
        pass

    def update_hide_state(self):
        hidden = self.obj.hide_get()  # or self.obj.users_collection[0].hide_viewport   # collection cannot work
        self.solid.hide_set(hidden)

    def transform(self):
        if self.obj:
            Solid(self.obj).transform()

    # private

    def check(self):
        if self.obj.type == 'MESH' and self.obj.soc_mesh_cut_type != 'None':
            return True
        elif self.obj.type == 'CURVE' and self.obj.soc_curve_cut_type != 'None':
            return True
        else:
            return False
