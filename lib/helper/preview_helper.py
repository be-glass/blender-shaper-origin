import bpy
from mathutils import Matrix, Vector

from ..constant import PREVIEW_Z, PREFIX
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

    m0 = obj.matrix_world if perimeter else Matrix()
    m1 = perimeter.matrix_world.inverted() if perimeter else Matrix()
    m2 = lift_z(context, obj)
    m3 = reference.matrix_world if reference else Matrix()
    m4 = bounding.matrix_world if bounding else Matrix()

    return m0, m1, m2, m3, m4


def lift_z(context, obj):
    if obj.soc_mesh_cut_type != 'None':
        z = PREVIEW_Z[obj.soc_mesh_cut_type]
    elif obj.soc_curve_cut_type != 'None':
        z = PREVIEW_Z[obj.soc_curve_cut_type]
    else:
        z = "0"
    lift = Vector([0, 0, length(context, z)])
    return Matrix.Translation(lift)


def get_bounding_frame():
    name = BOUNDING_FRAME_NAME
    if name in bpy.data.objects.keys():
        return bpy.data.objects[name]
    else:
        return None
