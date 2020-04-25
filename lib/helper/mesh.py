import bmesh
import bpy
from mathutils import Matrix, Vector

from .other import select_active, error_msg




def repair_mesh(context, obj):  # TODO: needed?
    active = context.object
    select_active(context, obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.editmode_toggle()
    bpy.ops.object.mode_set(mode='OBJECT')

    if active:
        select_active(context, active)


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


def add_plane(context, name, size, collection=None):  # TODO: replace without ops
    bpy.ops.mesh.primitive_plane_add(size=size)

    # delete face
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.context.object.data.polygons[0].select = True
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    select_active(context, context.object)  # TODO

    obj = context.active_object
    obj.name = name

    if collection:
        for c in obj.users_collection:
            c.objects.unlink(obj)
        collection.objects.link(obj)
    return obj


def curve2mesh(context, obj, name='', add_face=False):
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
