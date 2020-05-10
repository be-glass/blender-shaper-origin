import bpy
from typing import List

from bpy.types import Object, BlendDataObjects


class Project:

    @classmethod
    def name(self) -> str:
        name = (bpy.path.display_name_from_filepath(bpy.data.filepath))
        return name if name else "untitled"

    @classmethod
    def cut_objs(self) -> List[BlendDataObjects]:
        return [o for o in bpy.data.objects if o.soc_object_type == 'Cut']

    @classmethod
    def perimeter_objs(self) -> List[BlendDataObjects]:
        per_objs = [o for o in self.cut_objs() if o.soc_mesh_cut_type == 'Perimeter']
        return per_objs
