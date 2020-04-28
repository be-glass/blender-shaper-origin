import bpy
from enum import Enum

from .constant import PREFIX
from .helper.other import remove_by_name


class Collect(Enum):
    Internal = 'Internal'
    Solid = 'Solid'
    Reference = 'Reference'
    Preview = 'Preview'


class Collection:

    def __init__(self, name: Collect):
        self.type = name
        self.name = PREFIX + name.value
        self.collection = self.get_collection()

    def get(self):
        return bpy.data.collections[self.name]

    def collect(self, obj, name):
        self.remove(name)
        obj.name = name

        for c in obj.users_collection:
            c.objects.unlink(obj)
        self.collection.objects.link(obj)

    # private

    def get_collection(self):
        if self.name in bpy.data.collections.keys():
            return bpy.data.collections[self.name]
        else:
            if self.type == Collect.Internal:
                parent = bpy.context.scene.collection  # master scene
            else:
                parent = Collection(Collect.Internal).get()

            collection = bpy.data.collections.new(self.name)
            parent.children.link(collection)
            return collection

    def remove(self, obj_name):
        if obj_name in bpy.data.objects.keys():
            remove_by_name(obj_name)
