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

import bmesh
import bpy
from bpy.types import Mesh, Object

from .other import select_active, active_object



def shade_mesh_flat(obj) -> None:
    for f in obj.data.polygons:
        f.use_smooth = False


def polygon2mesh(polygon) -> Mesh:
    bm = bmesh.new()
    [bm.verts.new(v) for v in polygon]
    bm.faces.new(bm.verts)
    bm.normal_update()
    me = bpy.data.meshes.new("")
    bm.to_mesh(me)
    return me


def create_object(polygon, col=None, name='') -> Object:
    me = polygon2mesh(polygon)
    obj = bpy.data.objects.new(name, me)
    if col:
        col.objects.link(obj)
    return obj


def add_plane(name, size, col=None) -> Object:  # TODO: replace without ops
    bpy.ops.mesh.primitive_plane_add(size=size)

    obj = active_object()

    # delete face
    bpy.ops.object.mode_set(mode='EDIT')
    obj.data.polygons[0].select = True
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    select_active(obj)  # TODO

    obj.name = name

    if col:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
    return obj


def fill_polygon(mesh) -> None:
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.new(bm.verts)
    bm.to_mesh(mesh)
    bm.free()
