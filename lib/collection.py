import bpy
from enum import Enum

from .constant import PREFIX


class Collect(Enum):
    Internal = 'Internal'
    Solid = 'Solid'
    Reference = 'Reference'
    Preview = 'Preview'


class Collection:

    def __init__(self, collection_obj):
        self.collection = collection_obj

    @classmethod
    def by_name(cls, name):
        c = bpy.data.collections[name]
        return cls(bpy.data.collections[name])

    @classmethod
    def by_obj(cls, obj):
        c = obj.users_collection[0]
        return cls(obj.users_collection[0])

    @classmethod
    def by_enum(cls, collect):

        name = PREFIX + collect.value

        if name in bpy.data.collections.keys():
            c = bpy.data.collections[name]
        else:
            if collect is Collect.Internal:
                parent = bpy.context.scene.collection  # master scene
            else:
                parent = Collection.by_enum(Collect.Internal).get()

            c = bpy.data.collections.new(name)
            parent.children.link(collection)

        return cls(c)

    def get(self):
        return self.collection

    def collect(self, obj, name):

        self.remove(name)
        obj.name = name

        for c in obj.users_collection:
            c.objects.unlink(obj)
        self.collection.objects.link(obj)

    def perimeter_objs(self):
        objs = self.collection.objects
        p_objs = [o for o in objs if o.soc_mesh_cut_type == 'Perimeter' and o.soc_object_type == 'Cut']
        return p_objs

    def subtrahend_objs(self):
        objs = self.collection.objects
        s_objs = [o for o in objs if o.soc_mesh_cut_type != 'Perimeter' and o.soc_object_type == 'Cut']
        return s_objs

    # private

    def remove(self, name):
        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name])
