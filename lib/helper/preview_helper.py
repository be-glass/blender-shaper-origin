from mathutils import Matrix, Vector

from ..constant import PREVIEW_Z
from .other import length, find_first_perimeter
from .gen_helper import get_reference


def transform_preview(context, bounding_frame, perimeter, obj):
    reference = get_reference(context, perimeter)

    m0 = obj.matrix_world
    m1 = perimeter.matrix_world.inverted()
    m2 = lift_z(context, obj)
    m3 = reference.matrix_world
    m4 = bounding_frame.matrix_world

    return m4 @ m3 @ m2 @ m1 @ m0


def transform_export(context, obj):
    perimeter = find_first_perimeter(obj)
    reference = get_reference(context, perimeter)

    m0 = obj.matrix_world
    m1 = perimeter.matrix_world.inverted()
    m2 = lift_z(context, obj)
    m3 = reference.matrix_world

    return m3 @ m2 @ m1 @ m0


def lift_z(context, obj):
    if obj.soc_mesh_cut_type != 'None':
        z = PREVIEW_Z[obj.soc_mesh_cut_type]
    elif obj.soc_curve_cut_type != 'None':
        z = PREVIEW_Z[obj.soc_curve_cut_type]
    else:
        z = "0"
    lift = Vector([0, 0, length(context, z)])
    return Matrix.Translation(lift)
