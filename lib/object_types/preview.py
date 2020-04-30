import bpy

from .reference import Reference
from ..helper.other import get_object_safely


class Preview:

    def __init__(self, obj):
        self.obj = obj

        self.reference = Reference(obj)

    def transform(self, matrix):
        name = self.obj.soc_preview_name
        if name:
            preview = get_object_safely(name)
            preview.matrix_world = matrix

        def reset_preview_object(self):
            name = self.obj.name + '.preview'
            if name in bpy.data.objects.keys():
                bpy.data.objects.remove(bpy.data.object[name])


class PreviewPerimeter(Preview):
    def transform(self):
        self.preview.transform_reference(self.obj)
        self.preview.transform_siblings(self.obj)
        self.preview.update_bounding_frame()

    def setup(self):
        pass

    def update(self):
        pass
