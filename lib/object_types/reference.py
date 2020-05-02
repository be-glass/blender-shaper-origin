import bpy

from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX


class Reference:

    def __init__(self, perimeter):
        self.cut_obj = perimeter.obj

    def get(self):
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return self.create()

    @property
    def name(self):
        if not self.cut_obj.soc_reference_name:
            self.cut_obj.soc_reference_name = PREFIX + self.cut_obj.users_collection[0].name + '.reference'
        return self.cut_obj.soc_reference_name

    def matrix(self):
        return self.get().matrix_world.copy()

    # private

    def create(self):

        compartment = Compartment.by_enum(Collect.Reference)

        ref_obj = bpy.data.objects.new(self.name, None)
        ref_obj.location = self.cut_obj.location
        ref_obj.matrix_world = self.cut_obj.matrix_world
        ref_obj.matrix_world.identity()
        compartment.link_obj(ref_obj)
        ref_obj.empty_display_size = 5
        ref_obj.empty_display_type = 'PLAIN_AXES'
        ref_obj.soc_object_type = 'Reference'
        ref_obj.name = self.name
        ref_obj.hide_set(True)
        return ref_obj
