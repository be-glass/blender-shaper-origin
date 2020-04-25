from .base import Generator
from .proxy import Proxy
from ..fillet import Fillet
from ..helper.gen_helper import *
from ..helper.other import get_object_safely
from ..helper.svg import svg_material_attributes
from ..preview import Preview


class Perimeter(Generator):

    def setup(self):
        super().setup()

        self.obj.soc_object_type = 'Cut'

        self.fillet = Fillet(self.context, self.obj)
        self.fillet.create(outside=True)
        self.fillet.display_type = 'WIRE'

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.get_fillet_obj()
        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        types = ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']
        for cut_obj in find_siblings_by_type(types, sibling=self.obj):
            self.rebuild_boolean_modifier(self.obj, cut_obj)

        self.reference = get_reference(self.context, self.obj)

        if self.context.scene.so_cut.preview:
            Preview(self.context).add_object(self.obj, self.obj)

    def update(self):

        self.adjust_solidify_thickness()

        cutouts = find_siblings_by_type('Cutout', sibling=self.context.object)
        for cut in cutouts:
            cut.soc_cut_depth = self.obj.soc_cut_depth + self.length('1mm')

    def update_hide_state(self):
        hidden = self.obj.hide_get()  # or self.obj.users_collection[0].hide_viewport   # collection cannot work
        solid = get_object_safely(self.obj.soc_solid_name, report_error=False)
        if solid:
            solid.hide_set(hidden)

    def svg(self):
        fillet = Fillet(self.context, self.obj)
        fillet_obj = fillet.create(outside=True)
        proxy = Proxy(self.context, fillet_obj)
        proxy.setup_proxy(self.obj)

        content, z = self.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)

        return z, self.svg_object(content, attributes)
