import bpy
from mathutils import Matrix, Vector

from .reference import Reference
from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..helper.mesh_helper import create_object
from ..helper.other import length
from ..shape.perimeter import Perimeter

BOUNDING_FRAME_NAME = PREFIX + 'Bounding Frame'


class Bounding:

    def __init__(self):
        self.compartment = Compartment.by_enum(Collect.Internal)
        self.compartment = Compartment.by_enum(Collect.Internal)
        self.frame = self.reset()

    def reset(self):

        mw = self.old_matrix()
        quad = self.boundary_quad()
        frame = create_object(quad, self.compartment.get(), BOUNDING_FRAME_NAME)
        frame.matrix_world = mw
        frame.soc_object_type = "Bounding"
        return frame

    def transform(self):
        from .preview import Preview

        frame_mw = Bounding().matrix()

        for perimeter in Perimeter.all():

            perimeter_mw_1 = perimeter.matrix().inverted()
            reference_mw = Reference(perimeter).matrix()

            for preview_obj in perimeter.preview_objs():
                Preview(preview_obj).transform(perimeter_mw_1, reference_mw, frame_mw)

    def hide(self):
        self.frame.hide_set(True)

    def frame(self):
        return self.frame

    def matrix_inverted(self):
        return self.frame.matrix_world.inverted()

    def matrix(self):
        return self.frame.matrix_world.copy()

    # private

    def old_matrix(self):
        if BOUNDING_FRAME_NAME in bpy.data.objects.keys():
            return bpy.data.objects[BOUNDING_FRAME_NAME].matrix_world.copy()
        else:
            return Matrix()

    def boundary_quad(self):
        z = -0.1
        d = length('10mm')  # margin of preview sheet
        c0, c1 = boundaries()

        m0 = Vector([c1.x + d, c0.y - d, z])
        m1 = Vector([c1.x + d, c1.y + d, z])
        m2 = Vector([c0.x - d, c1.y + d, z])
        m3 = Vector([c0.x - d, c0.y - d, z])

        return [m0, m1, m2, m3]


# static

def boundaries():
    x = []
    y = []
    z = []

    for perimeter in Perimeter.all():

        reference = Reference(perimeter)
        user = reference.matrix()

        scale = Matrix.Diagonal(perimeter.matrix().to_scale()).to_4x4()

        bb = perimeter.obj.bound_box
        for p in range(8):
            v_local = Vector([bb[p][0], bb[p][1], bb[p][2]])

            v = user @ scale @ v_local

            x.append(v[0])
            y.append(v[1])
            z.append(v[2])

    minimum = Vector([min(x), min(y), min(z)])
    maximum = Vector([max(x), max(y), max(z)])
    return minimum, maximum
