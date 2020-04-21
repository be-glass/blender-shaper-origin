import bpy
from mathutils import Vector


def add_nurbs_square(collection, name):
    curve = bpy.data.curves.new(name, 'CURVE')
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.dimensions = "2D"

    square = [(0.5, 0), (0.5, -1), (-0.5, -1), (-0.5, 0)]

    spline = curve.splines.new('NURBS')
    spline.use_cyclic_u = True

    points = [square[i // 3] for i in range(3 * len(square))]
    spline.points.add(len(points) - 1)

    for (i, point) in enumerate(points):
        spline.points[i].co = Vector(point).to_4d()

    return obj
