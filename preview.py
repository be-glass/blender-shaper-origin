import bpy

from . import helper
from .helper import length, add_plane, get_preview_collection, select_active, apply_scale
from .preview_object import PreviewObject


class Preview:
    def __init__(self, context):
        self.context = context
        self.collection = get_preview_collection(self.context)
        self.perimeters = [o for o in bpy.data.objects if o.soc_mesh_cut_type == 'Perimeter']
        if self.perimeters:
            self.reference = self.get_bounding_frame()
        else:
            self.reference = None

    def create(self):
        if self.perimeters:
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
            x0, x1, y0, y1, z0, z1 = helper.boundaries(self.perimeters)

            quad = [[x0, y0, 0], [x0, y1, 0], [x1, y1, 0], [x1, y0, 0]]
            frame = helper.create_object(self.collection, quad, "Bounding Frame")
            frame.soc_object_type = "Bounding"
            return frame

    def add_objects(self):
        for obj in self.perimeters:
            PreviewObject().create(self.context, self.collection, obj, self.reference)
