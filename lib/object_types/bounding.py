import bpy
from mathutils import Matrix, Vector

from ..collection import Collection, Collect
from ..helper.gen_helper import boundaries
from ..helper.mesh_helper import create_object
from ..helper.other import get_object_safely, length, find_cuts, filter_perimeters
from ..helper.preview_helper import transform_preview, BOUNDING_FRAME_NAME


class Bounding:

    def __init__(self):
        self.cut_objs = find_cuts()
        self.perimeters = filter_perimeters(self.cut_objs)
        self.collection = Collection.by_enum(Collect.Internal).get()
        self.frame = self.reset()

    def reset(self):

        mw = self.old_matrix()
        quad = self.boundary_quad()
        frame = create_object(quad, self.collection.get(), BOUNDING_FRAME_NAME)
        frame.matrix_world = mw
        frame.soc_object_type = "Bounding"
        return frame

    def transform(self):

        for perimeter in self.perimeters:
            for obj in perimeter.users_collection[0].objects:

                if obj.soc_object_type == 'Cut':
                    matrix = transform_preview(obj, perimeter, self.frame.matrix_world)
                    preview_obj = get_object_safely(obj.soc_preview_name)
                    preview_obj.matrix_world = matrix

    def hide(self):
        frame = self.get_bounding_frame()
        if frame:
            frame.hide_set(True)

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
