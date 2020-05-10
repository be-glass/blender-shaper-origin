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

class Modifier:
    def __init__(self, obj) -> None:
        self.mod = obj.modifiers

    def subtract(self, subtrahend, name) -> None:
        self.remove(name)
        boolean = self.mod.new(name, 'BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = subtrahend

    def remove(self, name) -> None:
        for m in self.mod:
            if m.name == name:
                self.mod.remove(m)

    def exists(self, name) -> bool:
        return bool(name in [m.name for m in self.mod])

    def set_thickness(self, name, thickness) -> None:
        solidify = [m for m in self.mod if m.type == 'SOLIDIFY']
        if solidify:
            solidify[0].thickness = thickness
