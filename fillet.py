import math
from math import pi
import mathutils
from mathutils import Vector, Matrix

from .helper.mesh import create_object
from .helper.other import error_msg, warning_msg, get_solid_collection, delete_object
from .constant import PREFIX, FILLET_RESOLUTION


class Fillet:

    def __init__(self, context, obj):
        self.context = context
        self.obj = obj
        self.radius = obj.soc_tool_diameter / 2
        self.polygon = self.get_polygon_safely()
        self.resolution = FILLET_RESOLUTION
        self.name = PREFIX + self.obj.name + ".fillets"

    def get_polygon_safely(self):
        polygons = self.obj.data.polygons
        n = len(polygons)
        if n == 0:
            error_msg(f'Object "{self.obj.name}" has no face!')
            return None
        elif n > 1:
            warning_msg(f'Object "{self.obj.name}" has more than 1 faces! Using the first one.')
        return self.obj.data.polygons[0]

    # def get_obj(self):
    #     return get_object_safely(self.name)

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

    def is_inside(self, corner):
        A, B, C = corner
        abc_normal = (B - A).cross(C - B)
        d = abc_normal.dot(self.polygon.normal)
        return d > 0  # > 0 if inside, = 0 if straight

    def create(self, outside=False):
        fillet = []
        collection = get_solid_collection(self.context)

        for shift in range(self.corner_count()):
            corner = self.corner_vectors(shift)
            fillet += self.corner_fillet(corner, outside)

        delete_object(self.obj.soc_solid_name)

        fillet_obj = create_object(collection, fillet, self.name)
        fillet_obj.matrix_world = self.obj.matrix_world

        self.obj.soc_solid_name = fillet_obj.name

        self.obj.display_type = 'WIRE'

        fillet_obj.hide_select = True

        self.obj.soc_solid_name = fillet_obj.name

        return fillet_obj

    def corner_angle(self, corner):
        A, B, C = corner
        return (B - A).angle(C - B)

    def rounded(self, corner):
        A, B, C = corner

        abc_normal = mathutils.geometry.normal([C, B, A])

        ang_ABC = self.corner_angle(corner)
        k = self.radius / math.sin(ang_ABC)
        M = B + k * ((A - B).normalized() + (C - B).normalized())

        P = []
        MB1 = (B - M).normalized()
        for i in range(self.resolution):
            ang = - ang_ABC * (i / self.resolution - 0.5)
            rotation = Matrix.Rotation(ang, 4, abc_normal)
            P.append(M + self.radius * rotation @ MB1)
        return P

    def corner_fillet(self, corner, outside):
        corner_point = corner[1:2]

        if self.corner_angle(corner) < math.radians(5):
            return corner_point

        if self.is_inside(corner) ^ outside:
            if self.obj.soc_dogbone:
                return self.dogbone(corner)
            else:
                return self.rounded(corner)
        else:
            return corner_point

    def dogbone(self, corner):
        A, B, C = corner

        abc_normal = mathutils.geometry.normal([A, B, C])

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
