import bpy

from .object_types.cut import Cut
from .shape import Shape
from .shape.perimeter import Perimeter


class Project:

    def name(self):
        name = (bpy.path.display_name_from_filepath(bpy.data.filepath))
        return name if name else "untitled"

    def cut_objs(self):
        return [o for o in bpy.data.objects if o.soc_object_type == 'Cut']

    def shapes(self):
        return [Shape.factory(o) for o in self.cut_objs()]

    def cuts(self):
        return [Cut(o) for o in self.cut_objs()]

    def perimeter_objs(self):
        per_objs = [o for o in self.cut_objs() if o.soc_mesh_cut_type == 'Perimeter']
        return per_objs

    def perimeters(self):
        return [Perimeter(o) for o in self.perimeter_objs()]
