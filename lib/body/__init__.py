import bpy

from ..collection import Collection, Collect
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
        pass

    def defaults(self):
        self.shape = None

    def clean(self):
        delete_obj(self.name)
        Shape(self.cut_obj).clean()

    def update(self):
        self.shape_factory().update()

    def get(self):
        if self.name in bpy.data.objects.keys():
            return bpy.data.objects[self.name]
        else:
            return None

    def transform(self, matrix):
        obj = self.get()
        if obj:
            obj.matrix_world = matrix

    def hide(self):
        pass
        if self.obj:
            self.obj.hide_set(state)
