import math

from . import Shape
from ..collection import Collection
from ..helper.other import length


class MeshShape(Shape):

    def setup(self):
        self.obj.display_type = 'WIRE'

    def update(self):
        if self.obj.soc_mesh_cut_type == 'Cutout':

            perimeters = Collection.by_obj(self.obj).perimeter_objs()

            if perimeters:
                cutout_depth = perimeters[0].soc_cut_depth

                if not math.isclose(self.obj.soc_cut_depth, cutout_depth, abs_tol=length('0.01mm')):
                    self.obj.soc_cut_depth = cutout_depth


#
# def svg(self):
#
#     fillet = Fillet(self.self.obj)
#     fillet_obj = fillet.create()
#     proxy = Proxy(self.fillet_obj)
#     proxy.setup_proxy(self.obj)
#
#     content = proxy.svg_mesh()
#     attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
#     contents = self.svg_object(content, attributes)
#     z = lift_z(self.self.obj)
#
#     return z, contents
