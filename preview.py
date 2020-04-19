import bpy
from mathutils import Matrix, Vector

from . import helper, gen_helper
from .helper import length, add_plane, get_preview_collection, select_active, apply_scale





class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.perimeters = [o for o in bpy.data.objects if o.soc_mesh_cut_type == 'Perimeter']

    def create(self):
        if self.perimeters:
            self.bounding = self.update_bounding_frame()
            self.add_objects()
        else:
            self.bounding = None

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)
        self.hide_bounding_frame()

    def hide_bounding_frame(self):
        collection = helper.get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            search[0].hide_set(True)

    def update_bounding_frame(self):
        collection = helper.get_soc_collection(self.context)
        search = [o for o in collection.objects if o.name.startswith('Bounding Frame')]
        if search:
            mw = search[0].matrix_world.copy()
            bpy.data.objects.remove(search[0])
        else:
            mw = Matrix()

        m0, m2 = helper.boundaries(self.perimeters)

        m0.z = 0
        m2.z = 0
        m1 = Vector([m0.x, m2.y, 0])
        m3 = Vector([m2.x, m0.y, 0])
        quad = [m0, m1, m2, m3]

        frame = helper.create_object(collection, quad, "Bounding Frame")
        frame.matrix_world = mw
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
                reference_obj.location.negate()
