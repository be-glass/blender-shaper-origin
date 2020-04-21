import bpy
from mathutils import Vector


def add_nurbs_quad(collection, name, width=1, height=1):
    curve = bpy.data.curves.new(name, 'CURVE')
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    curve.dimensions = "2D"

    square = [(0, 0), (0, 1), (1, 1), (1, 0)]

    points = []
    for s in square:
        for i in range(3):
            points.append(s)

    npoints = len(points)

    spline = curve.splines.new('NURBS')
    spline.use_cyclic_u = True
    spline.points.add(npoints - 1)

    for (i, point) in enumerate(points):
        spline.points[i].co = Vector(point).to_4d()

    return obj
