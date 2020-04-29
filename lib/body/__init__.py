import bpy

from ..collection import Collection, Collect
from ..constant import PREFIX
from ..helper.other import delete_obj
from ..shape import Shape
from ..shape.curve_shape import Curve
from ..shape.mesh_guide import MeshGuide
from ..shape.mesh_shape import MeshShape
from ..shape.perimeter import Perimeter


class Body:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj
        self.defaults()

        # config
        self.cut_obj.soc_known_as = self.cut_obj.name
        self.name = PREFIX + self.cut_obj.name + ".body"
        self.collection = Collection.by_enum(Collect.Solid)
        self.shape = self.shape_factory(cut_obj)

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

    def shape_factory(_, cut_obj):
        shape = None

        if cut_obj.type == 'MESH':
            if cut_obj.soc_mesh_cut_type == 'Perimeter':
                shape = Perimeter
            elif cut_obj.soc_mesh_cut_type == 'GuideArea':
                shape = MeshGuide
            elif cut_obj.soc_mesh_cut_type:
                shape = MeshShape

        elif cut_obj.type == 'CURVE':
            if cut_obj.soc_curve_cut_type:
                shape = Curve

        return shape(cut_obj)
