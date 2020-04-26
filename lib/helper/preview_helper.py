import bpy
from mathutils import Matrix, Vector

from ..constant import STACK_Z, PREFIX, PREVIEW_STACK_DELTA
from .other import length
from .gen_helper import get_reference

BOUNDING_FRAME_NAME = PREFIX + 'Bounding Frame'

def transform_preview(context, obj, perimeter, bounding_frame):
    m0, m1, m2, m3, m4 = transforms(context, obj, perimeter, bounding_frame)
    return m4 @ m3 @ m2 @ m1 @ m0


def transform_export(context, obj, perimeter):
    m0, m1, m2, m3, _ = transforms(context, obj, perimeter)
    return m3 @ m2 @ m1 @ m0


def transforms(context, obj, perimeter, bounding=None):
    reference = get_reference(context, perimeter) if perimeter else None

    z = lift_z(context, obj)
    lift = Vector([0, 0, z * length(context, PREVIEW_STACK_DELTA)])

    m0 = obj.matrix_world.copy() if perimeter else Matrix()
    m1 = perimeter.matrix_world.inverted() if perimeter else Matrix()
    m2 = Matrix.Translation(lift)
    m3 = reference.matrix_world.copy() if reference else Matrix()
    m4 = bounding.matrix_world.copy() if bounding else Matrix()

    return m0, m1, m2, m3, m4


def lift_z(context, obj):
    if obj.soc_mesh_cut_type != 'None':
        z = STACK_Z[obj.soc_mesh_cut_type]
    elif obj.soc_curve_cut_type != 'None':
        z = STACK_Z[obj.soc_curve_cut_type]
    else:
        z = 0
    return z


def get_bounding_frame():
    name = BOUNDING_FRAME_NAME
    if name in bpy.data.objects.keys():
        return bpy.data.objects[name]
    else:
        return None
