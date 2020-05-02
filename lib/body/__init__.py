import bpy

from ..blender.collection import Collection, Collect
from ..constant import PREFIX
from ..helper.other import delete_obj
from ..shape import Shape


class Body:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj
        self.defaults()

        # config
        self.cut_obj.soc_known_as = self.cut_obj.name
        self.name = PREFIX + self.cut_obj.name + ".body"
        self.collection = Collection.by_enum(Collect.Solid)
        self.shape = Shape.factory(cut_obj)

    @classmethod
    def factory(_, cut_obj):

        from .mesh_body import MeshBody
        from .meshed_curve import MeshedCurve

        if cut_obj.soc_mesh_cut_type:
            body = MeshBody
        elif cut_obj.soc_curve_cut_type:
            body = MeshedCurve
        else:
            return None
        return body(cut_obj)

    def defaults(self):
        self.shape = None

    def clean(self):
        delete_obj(self.name)
        Shape(self.cut_obj).clean()

    def update(self):
        self.shape.update()

    def get(self):
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return None

    def transform(self, matrix):
        obj = self.get()
        if obj:
            obj.matrix_world = matrix

