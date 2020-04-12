import math
from math import pi
import mathutils
from mathutils import Vector, Matrix

from . import constant, helper, sim_helper
from .constant import Prefix

def update(context, obj):
    if obj.type == 'MESH':
        ct = obj.soc_mesh_cut_type
        dogbone = Fillet(obj)

        if not obj.soc_dogbone:
            dogbone.delete()
        elif ct in ['None', 'Guide']:
            dogbone.delete()

        elif ct in ['Cutout', 'Pocket']:
            dogbone.create()
        elif ct == 'Perimeter':
            dogbone.create(outside=True)
        else:
            helper.err_implementation(context)


class Fillet:

    def __init__(self, obj):
        self.obj = obj
        self.radius = obj.soc_tool_diameter / 2
        self.polygon = self.obj.data.polygons[0]
        self.resolution = constant.dogbone_resolution
        self.name = Prefix + self.obj.name + ".dogbone"

    def is_valid(self):
        if self.obj.soc_dogbone and \
                self.obj.type == 'MESH' and \
                self.obj.soc_mesh_cut_type in ['Cutout', 'Pocket', 'Perimeter']:
            return True
        else:
            return False

    def get_obj(self):
        return helper.get_object_safely(self.name)

    def delete(self):
        helper.delete_object(self.name)

    def create(self, outside=False):
        dogbone = []
        collection = sim_helper.get_internal_collection(self.obj)

        for shift in range(self.corner_count()):
            dogbone += self.regular_polygon(shift, outside)
        dogbone_obj = helper.create_object(collection, dogbone, self.name)
        dogbone_obj.matrix_world = self.obj.matrix_world

        self.obj.display_type = 'WIRE'

        return dogbone_obj

    def polygon_angles(self):
        angles = []
        m = self.obj.data
        corners = len(m.vertices)
        for i in range(corners):
            ab, cd = [e for e in m.edges if e.vertices[0] == i or e.vertices[1] == i]
            a, b = ab.vertices
            d, c = cd.vertices
            v_ab = Vector(m.vertices[a].co) - Vector(m.vertices[b].co)
            v_cd = Vector(m.vertices[c].co) - Vector(m.vertices[d].co)
            angles.append(v_ab.angle(v_cd))
        return angles

    def polygon_count(self):
        return len(self.obj.data.polygons)

    def corner_count(self):
        return len(self.polygon.vertices)

    def corner_vectors(self, shift=0):
        m = self.obj.data
        n = self.corner_count()
        if n < 3:
            return []

        index = [i for i in m.polygons[0].vertices]
        shifted = [index[(i + shift) % n] for i in range(n)]
        x = [Vector(m.vertices[i].co) for i in shifted]
        y = x[0:3]
        return y

    def is_inside(self, A, B, C):
        abc_normal = (B - A).cross(C - B)
        return abc_normal.dot(self.polygon.normal)  # > 0 if inside, = 0 if straight

    def regular_polygon(self, corner_index, outside=False):
        A, B, C = self.corner_vectors(corner_index)

        abc_normal = mathutils.geometry.normal([A, B, C])

        corner_sense = self.is_inside(A, B, C)
        if (corner_sense <= 0 and not outside) or (corner_sense >= 0 and outside):
            return [B]

        D = B + (C - B).normalized() + (A - B).normalized()

        rBD1 = self.radius * (D - B).normalized()
        M = B + rBD1

        p = []

        angle_ABM = rBD1.angle(A - B)
        angle_MBC = rBD1.angle(C - B)

        if angle_ABM < pi / 4:
            p.append(self.intersection_tangent_with_segment(A, B, M))
        else:
            p.append(self.intersection_circle_with_segment(A, B, M))
            pass  # add intersection point

        if angle_ABM < pi / 2:
            p += self.half_circle(M, rBD1, B, abc_normal, A - B, -pi / 2)

        p.append(B)

        if angle_MBC < pi / 2:
            p += self.half_circle(M, rBD1, B, abc_normal, -(C - B))

        if angle_MBC < pi / 4:
            p.append(self.intersection_tangent_with_segment(C, B, M))
        else:
            p.append(self.intersection_circle_with_segment(C, B, M))
            pass
        return p

    def intersection_tangent_with_segment(self, A, B, M):
        AB1 = (A - B).normalized()
        ang_ABM = (A - B).angle(M - B)
        r = (M - B).length
        S = B + r / math.cos(ang_ABM) * AB1
        X = B + r / (S - M).length * (S - B)

        return X

    def intersection_circle_with_segment(self, A, B, M):
        BA1 = (A - B).normalized()
        ang_ABM = (A - B).angle(M - B)
        r = (M - B).length

        length = 2 * r * self.regular_polygon_radius_factor() * math.cos(ang_ABM)

        return B + length * BA1

    def regular_polygon_radius_factor(self):
        a_step = 2 * pi / (self.resolution * 4)
        a_offset = a_step / 2
        return 1.0 / math.cos(a_offset)

    def half_circle(self, center_point, center_of_first_segment, corner_point, normal, boundary_axis, start_angle=0.0):
        a_step = 2 * pi / (self.resolution * 4)
        r_polygon = self.regular_polygon_radius_factor()
        p = []

        axis_plane_normal = Matrix.Rotation(pi / 2, 4, normal) @ boundary_axis

        for i in range(self.resolution):
            rotation = Matrix.Rotation(a_step * (i + 0.5) + start_angle, 4, normal)

            point = center_point - r_polygon * rotation @ center_of_first_segment

            d = mathutils.geometry.distance_point_to_plane(point, corner_point, axis_plane_normal)

            if not d < 0:
                p.append(point)

        return p
