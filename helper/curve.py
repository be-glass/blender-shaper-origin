import bpy
from mathutils import Vector

from .mesh import curve2mesh


def add_nurbs_square(collection, name, curve_cut_type):
    curve = bpy.data.curves.new(name, 'CURVE')
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.dimensions = "2D"

    square = [(0, 0), (1, 0), (1, 1), (0, 1)]

    if curve_cut_type == 'Exterior':
        shift = (-1, -1)
    elif curve_cut_type == 'Interior':
        shift = (0, -1)
    else:
        shift = (-0.5, -1)

    spline = curve.splines.new('NURBS')
    spline.use_cyclic_u = True

    points = [square[i // 3] for i in range(3 * len(square))]
    spline.points.add(len(points) - 1)

    for (i, point) in enumerate(points):
        spline.points[i].co = (Vector(point) + Vector(shift)).to_4d()

    return obj


def face_normal(context, obj):
    mesh_obj = curve2mesh(context, obj, add_face=True)
    normal = mesh_obj.data.polygons[0].normal
    return normal


def face_is_down(context, obj):
    return face_normal(context, obj).dot(Vector([0, 0, 1])) < 0
