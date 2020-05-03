import bpy
from enum import Enum

from ..constant import PREFIX


class Collect(Enum):
    Internal = 'Internal'
    Solid = 'Solid'
    Reference = 'Reference'
    Preview = 'Preview'
    Helper = 'Helper'


class Compartment:

    def __init__(self, collection_obj):
        self.col = collection_obj

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
                parent = Compartment.by_enum(Collect.Internal).get()

            c = bpy.data.collections.new(name)
            parent.children.link(c)

        return cls(c)

    def objects(self):
        return self.col.objects

    def get(self):
        return self.col

    def link(self, obj):
        self.col.objects.link(obj)

    def collect(self, obj, name, reset=True):

        if reset:
            self.remove(name)

        obj.name = name

        for c in obj.users_collection:
            c.objects.unlink(obj)
        self.col.objects.link(obj)

    def perimeter_objs(self):
        objs = self.col.objects
        p_objs = [o for o in objs if o.soc_mesh_cut_type == 'Perimeter' and o.soc_object_type == 'Cut']
        return p_objs

    def subtrahend_objs(self):
        objs = self.col.objects
        s_objs = [o for o in objs if o.soc_mesh_cut_type != 'Perimeter' and o.soc_object_type == 'Cut']
        return s_objs

    # private

    def remove(self, name):
        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.objects[name])

    def link_obj(self, obj):
        self.col.objects.link(obj)

    def move(self, obj):
        [c.objects.unlink(obj) for c in obj.users_collection]
        self.col.objects.link(obj)


def delete_solid_objects(obj):
    for o in Compartment.by_enum(Collect.Solid).objects():
        if o.name == PREFIX + obj.name + ".fillets":
            bpy.data.objects.remove(o, do_unlink=True)


def cleanup_meshes(mesh_name):
    for o in Compartment.by_enum(Collect.Solid).objects():
        if o.name.startswith(mesh_name):
            bpy.data.objects.remove(o, do_unlink=True)
