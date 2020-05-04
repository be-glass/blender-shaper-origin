import bpy
from bpy.types import Object, BlendDataObjects
from mathutils import Matrix

from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX


class Reference:

    def __init__(self, perimeter) -> None:
        self.cut_obj = perimeter.obj

    def get(self) -> BlendDataObjects:
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return self.create()

    @property
    def name(self) -> str:
        if not self.cut_obj.soc_reference_name:
            self.cut_obj.soc_reference_name = PREFIX + self.cut_obj.users_collection[0].name + '.reference'
        return self.cut_obj.soc_reference_name

    def matrix(self) -> Matrix:
        return self.get().matrix_world.copy()

    # private

    def create(self) -> Object:

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
