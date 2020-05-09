from bpy.types import Object

from .__init__ import Shape
from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..helper.curve import add_nurbs_square
from ..helper.other import get_object_safely, remove_object


class Curve(Shape):

    def setup(self) -> None:
        self.obj.display_type = 'WIRE'


    def transform(self) -> None:
        solid_obj = get_object_safely(self.obj.soc_solid_name, report_error=False)
        if solid_obj:
            solid_obj.matrix_world = self.obj.matrix_world

    def get_bevel_object(self) -> Object:
        if self.obj.soc_bevel_name:
            bevel_obj = get_object_safely(self.obj.soc_bevel_name, report_error=False)
            if bevel_obj:
                return bevel_obj

        collection = Compartment.by_enum(Collect.Helper)

        name = f'{PREFIX}{self.obj.name}.bevel'
        remove_object(name)
        bevel_obj = add_nurbs_square(collection, name, self.obj.soc_curve_cut_type)
        bevel_obj.soc_object_type = 'Helper'
        bevel_obj.hide_set(True)
        self.obj.soc_bevel_name = bevel_obj.name

        return bevel_obj

# def svg(self):
#
#     mesh_obj = curve2mesh(self.self.obj, add_face=True)
#     proxy = Proxy(self.mesh_obj)
#     proxy.setup_proxy(self.obj)
#
#     content = proxy.svg_mesh()
#     attributes = svg_material_attributes(self.obj.soc_curve_cut_type)
#     z = lift_z(self.self.obj)
#
#     return z, self.svg_object(content, attributes)
