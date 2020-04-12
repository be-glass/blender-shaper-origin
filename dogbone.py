import bmesh
import bpy, math
import mathutils
from math import pi

from bpy import utils
from bpy.types import Panel, Operator
from mathutils import Vector

bl_info = {
    "name": "Dogbone Experiment",
    "author": "Boris Glass",
    "blender": (2, 80, 0),
    "version": (0, 0, 0),
    "location": "3D View > Sidebar",
    "description": "Prototyping some dogbone fillets",
    # "wiki_url": "https://docs.blender.org/manual/en/dev/addons/mesh/3d_print_toolbox.html",
    # "support": 'OFFICIAL',
    "category": "Mesh",
}

dogbone_resolution = 8


# init


def register():
    utils.register_class(BG_PT_Dogbone)
    utils.register_class(MESH_OT_refresh)


def unregister():
    utils.unregister_class(BG_PT_Dogbone)
    utils.unregister_class(MESH_OT_refresh)


# properties

# ui


def panels():
    return [BG_PT_Dogbone]


class DobgonePanel:
    bl_category = "Dogbone"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class BG_PT_Dogbone(DobgonePanel, Panel):
    bl_label = "Dogbone"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        layout.label(text="Hello Blender :-)")
        layout.operator("mesh.dogbone_refresh")
        layout.label(text="All done?")


# operators

class MESH_OT_refresh(Operator):
    bl_idname = "mesh.dogbone_refresh"
    bl_label = "Dogbone Refresh"
    bl_description = "Add dogbone fillets to active object with a signle Ngon."

    def execute(self, context):
        adam = bpy.data.objects['Adam']

        obj = create_dogbone(adam, 3.0)

        self.report({'INFO'}, "Finished with nothing")
        return {'FINISHED'}


def create_dogbone(obj, r):
    dogbone = []

    for shift in range(corner_count(obj.data.polygons[0])):
        dogbone += regular_polygon(obj, r, shift)
    dogbone_obj = create_object(obj.users_collection[0], dogbone)
    dogbone_obj.matrix_world = obj.matrix_world
    return dogbone_obj


def create_object(collection, polygon):
    bm = bmesh.new()
    [bm.verts.new(v) for v in polygon]
    bm.faces.new(bm.verts)
    bm.normal_update()
    me = bpy.data.meshes.new("")
    bm.to_mesh(me)
    obj = bpy.data.objects.new("Dogbone", me)
    collection.objects.link(obj)
    return obj


def remove_old_eve():
    if 'Eve' in bpy.data.objects.keys():
        eve = bpy.data.objects['Eve']
        bpy.data.objects.remove(eve)


def create_eve():
    adam = bpy.data.objects['Adam']
    eve = adam.copy()
    eve.name = "Eve"
    adam.users_collection[0].objects.link(eve)
    return eve


def add_Empty_at(location):
    bpy.ops.object.add(type='EMPTY', location=location)


def polygon_angles(obj):
    angles = []
    m = obj.data
    corners = len(m.vertices)
    for i in range(corners):
        ab, cd = [e for e in m.edges if e.vertices[0] == i or e.vertices[1] == i]
        a, b = ab.vertices
        d, c = cd.vertices
        v_ab = Vector(m.vertices[a].co) - Vector(m.vertices[b].co)
        v_cd = Vector(m.vertices[c].co) - Vector(m.vertices[d].co)
        angles.append(v_ab.angle(v_cd))
    return angles


def polygon_count(obj):
    return len(obj.data.polygons)


def corner_count(polygon):
    return len(polygon.vertices)


def corner_vectors(obj, shift=0):
    m = obj.data
    n = corner_count(m.polygons[0])
    if n < 3:
        return []

    index = [i for i in m.polygons[0].vertices]
    shifted = [index[(i + shift) % n] for i in range(n)]
    x = [Vector(m.vertices[i].co) for i in shifted]
    y = x[0:3]
    return y


def is_inside(A, B, C, polygon_normal):
    abc_normal = (B - A).cross(C - B)
    return abc_normal.dot(polygon_normal)  # > 0 if inside, = 0 if straight


def regular_polygon(obj, r, corner_index, outside=False):
    A, B, C = corner_vectors(obj, corner_index)

    poly_normal = obj.data.polygons[0].normal
    abc_normal = mathutils.geometry.normal([A, B, C])

    corner_sense = is_inside(A, B, C, poly_normal)
    if (corner_sense <= 0 and not outside) or (corner_sense >= 0 and outside):
        return [B]

    D = B + (C - B).normalized() + (A - B).normalized()

    rBD1 = r * (D - B).normalized()
    M = B + rBD1

    p = []

    angle_ABM = rBD1.angle(A - B)
    angle_MBC = rBD1.angle(C - B)

    if angle_ABM < pi / 4:
        p.append(intersection_tangent_with_segment(A, B, M))
    else:
        p.append(intersection_circle_with_segment(A, B, M))
        pass  # add intersection point

    if angle_ABM < pi / 2:
        p += half_circle(M, rBD1, B, abc_normal, A - B, -pi / 2)

    p.append(B)

    if angle_MBC < pi / 2:
        p += half_circle(M, rBD1, B, abc_normal, -(C - B))

    if angle_MBC < pi / 4:
        p.append(intersection_tangent_with_segment(C, B, M))
    else:
        p.append(intersection_circle_with_segment(C, B, M))
        pass
    return p


def intersection_tangent_with_segment(A, B, M):
    AB1 = (A - B).normalized()
    ang_ABM = (A - B).angle(M - B)
    r = (M - B).length
    S = B + r / math.cos(ang_ABM) * AB1
    X = B + r / (S - M).length * (S - B)

    return X


def intersection_circle_with_segment(A, B, M):
    BA1 = (A - B).normalized()
    ang_ABM = (A - B).angle(M - B)
    r = (M - B).length

    length = 2 * r * regular_polygon_radius_factor() * math.cos(ang_ABM)

    return B + length * BA1


def regular_polygon_radius_factor():
    a_step = 2 * pi / (dogbone_resolution * 4)
    a_offset = a_step / 2
    return 1.0 / math.cos(a_offset)


def half_circle(center_point, center_of_first_segment, corner_point, normal, boundary_axis, start_angle=0.0):
    a_step = 2 * pi / (dogbone_resolution * 4)
    r_polygon = regular_polygon_radius_factor()
    p = []

    axis_plane_normal = mathutils.Matrix.Rotation(pi / 2, 4, normal) @ boundary_axis

    for i in range(dogbone_resolution):
        rotation = mathutils.Matrix.Rotation(a_step * (i + 0.5) + start_angle, 4, normal)

        point = center_point - r_polygon * rotation @ center_of_first_segment

        d = mathutils.geometry.distance_point_to_plane(point, corner_point, axis_plane_normal)

        if not d < 0:
            p.append(point)

    return p
