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

from .other import select_active, error_msg, active_object


def repair_mesh(obj):  # TODO: needed?
    active = active_object()
    select_active(obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.mode_set(mode='OBJECT')

    if active:
        select_active(active)


def shade_mesh_flat(obj):
    for f in obj.data.polygons:
        f.use_smooth = False


def create_object(polygon, collection=None, name=''):
    bm = bmesh.new()
    [bm.verts.new(v) for v in polygon]
    bm.faces.new(bm.verts)
    bm.normal_update()
    me = bpy.data.meshes.new("")
    bm.to_mesh(me)
    obj = bpy.data.objects.new(name, me)
    if collection:
        collection.objects.link(obj)
    return obj


def add_plane(name, size, collection=None):  # TODO: replace without ops
    bpy.ops.mesh.primitive_plane_add(size=size)

    obj = active_object()

    # delete face
    bpy.ops.object.mode_set(mode='EDIT')
    obj.data.polygons[0].select = True
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    select_active(obj)  # TODO

    obj.name = name

    if collection:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def curve2mesh(obj, name='', add_face=False):
    context = bpy.context
    depsgraph = context.evaluated_depsgraph_get()
    object_evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(object_evaluated)
    mesh_obj = bpy.data.objects.new(name, mesh)
    mesh_obj.matrix_world = obj.matrix_world

    if add_face:
        fill_polygon(mesh_obj)

    mesh_obj.data.update()
    if mesh_obj.data.validate():
        error_msg('Curve to mesh conversion yielded invalid data!', context)

    return mesh_obj


def fill_polygon(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.new(bm.verts)
    bm.to_mesh(obj.data)
    bm.free()
