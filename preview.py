import bpy

from . import helper, gen_helper
from .helper import length, add_plane, get_preview_collection, select_active, apply_scale





class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.perimeters = [o for o in bpy.data.objects if o.soc_mesh_cut_type == 'Perimeter']
        if self.perimeters:
            self.bounding = self.get_bounding_frame()
        else:
            self.bounding = None

    def create(self):
        if self.perimeters:
            self.add_objects()

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)

    def get_bounding_frame(self):
        collection = helper.get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            return search[0]
        else:
            x0, y0, z0, x1, y1, z1 = helper.boundaries(self.perimeters)

            quad = [[x0, y0, 0], [x0, y1, 0], [x1, y1, 0], [x1, y0, 0]]
            frame = helper.create_object(collection, quad, "Bounding Frame")
            frame.soc_object_type = "Bounding"
            return frame

    def add_objects(self):
        for perimeter in self.perimeters:
            self.add_object(perimeter)

    def add_object(self, cut_obj):

        q = cut_obj.copy()
        q.data = cut_obj.data.copy()
        self.collection.objects.link(q)
        q.soc_object_type = 'Preview'
        helper.apply_scale(self.context, q)

        reference = gen_helper.get_reference(cut_obj)

        m = reference.matrix_world @ self.bounding.matrix_world

        q.matrix_world = m

        cut_obj.soc_preview_name = q.name

        return q

    def transform_reference(self, preview_obj):
        matches = [o for o in bpy.data.objects if o.soc_preview_name == preview_obj.name]
        if matches:
            obj = matches[0]
            reference_obj = helper.get_object_safely(obj.soc_reference_name, error_msg=False)
            if reference_obj is not None:
                mw = preview_obj.matrix_world.copy()
                mw.invert()
                reference_obj.matrix_world = mw
