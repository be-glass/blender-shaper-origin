import math

from typing import Tuple

from .__init__ import Shape
from ..blender.compartment import Compartment
from ..blender.fillet import Fillet
from ..blender.svg import SVG
from ..helper.other import length, z_lift, find_first_perimeter, svg_material_attributes, get_object_safely


class MeshShape(Shape):

    def setup(self) -> None:
        self.obj.display_type = 'WIRE'

    def update(self) -> None:
        if self.obj.soc_mesh_cut_type == 'Cutout':

            perimeters = Compartment.by_obj(self.obj).perimeter_objs()

            if perimeters:
                cutout_depth = perimeters[0].soc_cut_depth

                if not math.isclose(self.obj.soc_cut_depth, cutout_depth, abs_tol=length('0.01mm')):
                    self.obj.soc_cut_depth = cutout_depth

    def svg(self) -> Tuple[float, str]:

        is_outside = bool(self.obj.soc_mesh_cut_type in ['Perimeter', 'Exterior'])

        fillet_obj = Fillet(self.obj).create(rounded=False, outside=is_outside)
        fillet_obj.matrix_world = self.obj.matrix_world

        perimeter_obj = find_first_perimeter(self.obj)
        reference_obj = get_object_safely(perimeter_obj.soc_reference_name)

        svg = SVG(fillet_obj, perimeter_obj, reference_obj)
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)

        content = svg.svg_mesh()
        contents = self.svg_object(content, attributes)

        svg.clean()

        z = z_lift(self.obj)

        return z, contents

