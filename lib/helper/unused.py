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

from mathutils import Vector

# def polygon_angles(self):
#     angles = []
#     m = self.obj.data
#     corners = len(m.vertices)
#     for i in range(corners):
#         ab, cd = [e for e in m.edges if e.vertices[0] == i or e.vertices[1] == i]
#         a, b = ab.vertices
#         d, c = cd.vertices
#         v_ab = Vector(m.vertices[a].co) - Vector(m.vertices[b].co)
#         v_cd = Vector(m.vertices[c].co) - Vector(m.vertices[d].co)
#         angles.append(v_ab.angle(v_cd))
#     return angles


# def polygon_count(self):
#     return len(self.obj.data.polygons)

# def add_Empty_at(*location):
#     bpy.ops.object.add(type='EMPTY', location=(location))


# def transform_if_needed(obj, coordinates):
#     if obj.soc_reference_frame == 'local':
#         return coordinates
#     elif obj.soc_reference_frame == 'object':
#         return 'TODO'  # a feature missing implementation. TODO will be printed into the SVG file
#     else:  # 'global'
#         return obj.matrix_world @ coordinates

# def apply_mesh_scale(context, obj):
#     S = Matrix.Diagonal(obj.matrix_world.to_scale())
#
#     for v in obj.data.vertices:
#         v.co = S @ v.co
#
#     obj.scale = Vector([1, 1, 1])  # TODO: Does it work at all?
