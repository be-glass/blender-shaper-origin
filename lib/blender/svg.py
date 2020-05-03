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

from ..helper.other import vector2string


class SVG:

    def __init__(self, obj, perimeter_obj, reference_obj):
        self.obj = obj
        self.perimeter_mw_1 = perimeter_obj.matrix_world.inverted()
        self.reference_mw = reference_obj.matrix_world

    def svg_polygon(self, polygon):
        points = [self.obj.data.vertices[i] for i in polygon.vertices]
        return self.svg_path(points, is_closed=True)

    def svg_path(self, points, is_closed):
        source = ''
        path_cmd = 'M'
        for point in points:
            vector = self.reference_mw @ self.perimeter_mw_1 @ self.obj.matrix_world @ point.co
            source += path_cmd + vector2string(vector)
            path_cmd = 'L'
        if is_closed:
            source += 'Z'
        return f'<path d="{source}"/>'

    def svg_mesh(self):
        content = ''
        for polygon in self.obj.data.polygons:
            c = self.svg_polygon(polygon)
            content += c
        return content

    def clean(self):
        if self.obj:
            bpy.data.objects.remove(self.obj)
