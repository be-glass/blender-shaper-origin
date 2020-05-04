from typing import TypeVar, List

from ..blender.project import Project

T = TypeVar('T', bound='Shape')


class Shape:
    def __init__(self, obj) -> None:
        self.obj = obj
        self.obj.soc_known_as = self.obj.name

    @classmethod
    def factory(_, cut_obj) -> T:

        from .mesh_guide import MeshGuide
        from .mesh_shape import MeshShape
        from .perimeter import Perimeter
        from .curve_shape import Curve

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

    @classmethod
    def all(self) -> List[T]:
        return [Shape.factory(o) for o in Project.cut_objs()]

    def setup(self) -> None:
        self.obj.display_type = 'TEXTURED'
        pass

    def update(self) -> None:
        pass

    def clean(self) -> None:
        self.obj.display_type = 'TEXTURED'
        pass

    ### private

    def is_exterior(self) -> bool:
        return False

    def is_perimeter(self) -> bool:
        return False

    def is_guide(self) -> bool:
        return False
