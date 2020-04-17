import bpy

from .helper import length, add_plane, get_preview_collection, select_active, apply_scale


class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.reference = self.get_bounding_frame()

    def create(self):
        self.add_objects()

    def delete(self):
        for obj in self.collection.objects:
            bpy.data.objects.remove(obj)
        bpy.data.collections.remove(self.collection)

    def get_bounding_frame(self):
        search = [o for o in self.collection.objects if o.name.startswith('Bounding frame')]
        if search:
            return search[0]
        else:
            frame =  add_plane(self.context, "Bounding frame", length(self.context, '20cm'), collection=self.collection)
            frame.soc_object_type = "Bounding"
            return frame

    def add_objects(self):
        perimeters = [o for o in bpy.data.objects if o.soc_mesh_cut_type == 'Perimeter']
        for perimeter in perimeters:
            self.add_object(perimeter)


    def add_object(self, obj):
        pass
        # q = obj.copy()
        # q.data = obj.data.copy()
        # self.collection.objects.link(q)
        #
        # apply_scale(self.context, q)
        # q.matrix_world = self.reference.matrix_world
        # q.soc_object_type = 'Preview'

def exist_object(name):
    return bool(name in bpy.data.objects.keys())

def exist_collection(name):
    return bool(name in bpy.data.collections.keys())
