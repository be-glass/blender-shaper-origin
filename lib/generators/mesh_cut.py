import math

from .base import Generator
from .proxy import Proxy
from ..fillet import Fillet
from ..helper.gen_helper import *
from ..helper.svg import svg_material_attributes


class MeshCut(Generator):

    def setup(self):
        super().setup()
        self.obj.soc_object_type = 'Cut'

        self.fillet = Fillet(self.context, self.obj)
        self.fillet.create()
        self.fillet.display_type = 'WIRE'

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.get_fillet_obj()

        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection)

    def update(self):

        cut_type = self.obj.soc_mesh_cut_type

        if cut_type == 'Cutout':

            thickness = perimeter_thickness(self.obj)
            if thickness:
                cutout_depth = thickness + self.length('1mm')
            else:
                cutout_depth = self.length('1cm')

            if not math.isclose(self.obj.soc_cut_depth, cutout_depth, abs_tol=self.length('0.01mm')):
                self.obj.soc_cut_depth = cutout_depth
                return

            delta = 0.0
        elif cut_type == 'Pocket':
            delta = self.length('0.1mm')
        else:
            delta = 0.0

        self.adjust_solidify_thickness(delta=delta)

    def svg(self):

        fillet = Fillet(self.context, self.obj)
        fillet_obj = fillet.create(outside=True)
        proxy = Proxy(self.context, fillet_obj)
        proxy.setup_proxy(self.obj)

        content, z = proxy.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)

        return z, self.svg_object(content, attributes)
