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
from typing import List, TypeVar

from . import Bounding
from .solid import Solid
from ..blender.project import Project
from ..shape import Shape

T = TypeVar('T', bound='Cut')


class Cut:

    @classmethod
    def all(cls) -> List[T]:
        return [cls(o) for o in Project.cut_objs()]

    def __init__(self, obj) -> None:
        self.obj = obj
        self.defaults()
        self.valid = self.check()

    def defaults(self) -> None:
        # self.obj.soc_object_type = 'None'
        self.solid = None
        self.preview = None

    def reset(self) -> None:
        self.clean()
        self.defaults()
        self.setup()
        self.update()

    def clean(self) -> None:
        Solid(self.obj).clean()
        # self.preview.cleanup()

    def setup(self) -> None:

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
            self.preview = Preview()
            self.preview.setup(self.obj)

    def update(self) -> None:
        Solid(self.obj).update()
        # self.preview.update()     #?
        pass

    def svg(self) -> Shape:
        return Shape.factory(self.obj).svg()

    def update_hide_state(self) -> None:
        hidden = self.obj.hide_get()  # or self.obj.users_collection[0].hide_viewport   # collection cannot work
        self.solid.hide_set(hidden)

    def transform(self) -> None:
        if self.obj:
            Solid(self.obj).transform()
            Bounding().transform()

    # private

    def check(self) -> bool:
        if self.obj.type == 'MESH' and self.obj.soc_mesh_cut_type != 'None':
            return True
        elif self.obj.type == 'CURVE' and self.obj.soc_curve_cut_type != 'None':
            return True
        else:
            return False
