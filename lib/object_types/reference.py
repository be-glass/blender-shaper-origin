import bpy
from mathutils import Matrix

from .bounding import Bounding
from ..collection import Collection, Collect
from ..constant import PREFIX


class Reference:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj

    def get(self):
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return self.create()

    @property
    def name(self):
        if not self.cut_obj.soc_reference_name:
            self.cut_obj.soc_reference_name = PREFIX + self.cut_obj.users_collection[0].name + '.reference'
        return self.obj.soc_reference_name

    def matrix(self):
        return self.get().matrix_world.copy()

    # private

    def create(self):

        collection = Collection.by_enum(Collect.Reference)

        reference = bpy.data.objects.new(self.name, None)
        reference.location = self.cut_obj.location
        reference.matrix_world = self.cut_obj.matrix_world
        reference.matrix_world.identity()
        collection.objects.link(reference)
        reference.empty_display_size = 5
        reference.empty_display_type = 'PLAIN_AXES'
        reference.soc_object_type = 'Reference'
        reference.name = self.name
        reference.hide_set(True)
        return reference

    def transform(self, preview_obj):
        obj = self.get()
        obj.matrix_world = Bounding.matrix_inverted() @ preview_obj.matrix_world
        obj.location.z = 0
