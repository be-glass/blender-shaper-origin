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

from ..body import Body
from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..blender.modifier import Modifier


class Solid:

    def __init__(self, cut_obj) -> None:
        self.cut_obj = cut_obj
        self.defaults()

        self.mod_solidify_name = PREFIX + 'Solidify'
        self.mod_boolean_name = PREFIX + 'Boolean.' + self.cut_obj.name
        self.body = Body.factory(cut_obj)

    def defaults(self) -> None:
        self.solidify_name = None
        self.body = None

    def setup(self) -> None:
        # self.compartment = Compartment.by_enum(Collect.Solid)

        self.body.setup()

        if self.body.is_solid():
            self.solidify()
            self.subtract_from_perimeter()

    def update(self) -> None:
        body = Body.factory(self.cut_obj)
        if body:
            body.update()
            self.set_thickness()
            if self.cut_obj.type == 'CURVE':
                self.subtract_from_perimeter()

    def clean(self) -> None:
        Body(self.cut_obj).clean()
        self.defaults()

    def transform(self) -> None:
        if self.cut_obj and self.body:
            matrix = self.cut_obj.matrix_world
            self.body.transform(matrix)

    def subtract(self, other_body, modifier_name) -> None:
        minuend = self.body.get()
        subtrahend = other_body.get()
        if minuend and subtrahend:
            Modifier(minuend).subtract(subtrahend, modifier_name)

            # subtrahend.hide_set(True)   # TODO: activate later

    # private

    def subtract_from_perimeter(self) -> None:
        if not self.cut_obj:
            return

        if self.body and self.body.shape:
            if self.body.shape.is_perimeter():
                subtrahend_objs = Compartment.by_obj(self.cut_obj).subtrahend_objs()
                for s_obj in subtrahend_objs:
                    solid = Solid(s_obj)
                    self.subtract(solid.body, solid.mod_boolean_name)

            else:
                perimeter_objs = Compartment.by_obj(obj=self.cut_obj).perimeter_objs()
                if perimeter_objs:
                    Solid(perimeter_objs[0]).subtract(self.body, self.mod_boolean_name)

    def solidify(self) -> None:
        if self.cut_obj.type == 'MESH':
            self.body.obj.modifiers.new(self.mod_solidify_name, 'SOLIDIFY')

    def set_thickness(self) -> None:
        if self.cut_obj.type == 'MESH' and self.body:
            body_obj = self.body.get()
            if body_obj:
                Modifier(body_obj).set_thickness(self.mod_solidify_name,
                                                 self.cut_obj.soc_cut_depth + self.body.thickness_delta())
