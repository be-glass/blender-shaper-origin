from typing import TypeVar, Union

import bpy
from bpy.types import Object, BlendDataObjects

from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..helper.other import remove_object
from ..shape import Shape

T = TypeVar('T', bound='Body')

class Body:

    def __init__(self, cut_obj) -> None:
        self.cut_obj = cut_obj
        self.defaults()
        self.obj = None

        # config
        self.cut_obj.soc_known_as = self.cut_obj.name
        self.name = PREFIX + self.cut_obj.name + ".body"
        self.compartment = Compartment.by_enum(Collect.Solid)
        self.shape = Shape.factory(cut_obj)

    @classmethod
    def factory(_, cut_obj) -> Union[T, None]:

        from .mesh_body import MeshBody
        from .meshed_curve import MeshedCurve

        if cut_obj.soc_mesh_cut_type != 'None':
            body = MeshBody
        elif cut_obj.soc_curve_cut_type != 'None':
            body = MeshedCurve
        else:
            return None
        return body(cut_obj)

    def defaults(self) -> None:
        self.shape = None

    def clean(self) -> None:
        remove_object(self.name)
        Shape(self.cut_obj).clean()


    def get(self) -> Union[BlendDataObjects, None]:
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return None

    def transform(self, matrix) -> None:
        obj = self.get()
        if obj:
            obj.matrix_world = matrix

    def thickness_delta(self) -> float:
        return 0.0
