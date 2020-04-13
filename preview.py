import bpy

from .helper import length, add_plane, get_preview_collection, select_active, apply_scale


class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)

    def create(self):
        self.reference = self.add_bounding_frame()
        self.add_objects()

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)

    def add_bounding_frame(self):
        return add_plane(self.context, "Bounding frame", length(self.context, '20cm'), collection=self.collection)

    def add_objects(self):
        perimeters = [o for o in bpy.data.objects if o.soc_mesh_cut_type == 'Perimeter']
        for p in perimeters:
            q = p.copy()
            q.data = p.data.copy()
            self.collection.objects.link(q)

            select_active(self.context, q)
            apply_scale()
            q.matrix_world = self.reference.matrix_world







def exist_object(name):
    return bool(name in bpy.data.objects.keys())

def exist_collection(name):
    return bool(name in bpy.data.collections.keys())
