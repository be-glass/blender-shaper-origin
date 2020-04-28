from ..body import Body
from ..body.mesh_body import MeshBody
from ..body.meshed_curve import MeshedCurve
from ..collection import Collection, Collect
from ..constant import PREFIX
from ..helper.other import err_implementation


class Solid:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj
        self.defaults()

    def defaults(self):
        self.solidify_name = None
        self.body = None
        self.mod_solidify = None
        self.mod_boolean = None

    def setup(self):
        # config
        self.mod_solidify_name = PREFIX + 'Solidify'
        self.mod_boolean_name = PREFIX + 'Boolean.' + self.cut_obj.name

        # build
        self.body = self.body_factory()
        self.body.setup()

        # extrude
        if self.body and self.body.is_solid():
            self.mod_solidify = self.body.obj.modifiers.new(self.mod_solidify_name, 'SOLIDIFY')

    def update(self):
        if self.body:
            self.body.update()
            self.set_thickness()

    def clean(self):
        Body(self.cut_obj).clean()
        self.defaults()

    # private

    def body_factory(self):
        if self.cut_obj.soc_mesh_cut_type:
            body = MeshBody
        elif self.cut_obj.soc_curve_cut_type:
            body = MeshedCurve
        else:
            err_implementation()
            return None
        return body(self.cut_obj)

    def set_thickness(self, delta=0.0):
        if self.mod_solidify:
            self.mod_solidify.thickness = self.cut_obj.soc_cut_depth + delta

    def hide_set(self, state):
        pass
        # if self.obj:
        #     self.obj.hide_set(state)

# def adjust_boolean_modifiers(self, collection):
#     for perimeter_obj in find_perimeters(collection):
#         self.rebuild_boolean_modifier(perimeter_obj, self.obj)
#
#
#
# def rebuild_boolean_modifier(self, perimeter_obj, subtract_obj):
#     modifier_name = boolean_modifier_name(subtract_obj)
#
#     subtract_fillet = self.get_fillet_obj(subtract_obj)
#     perimeter_fillet = self.get_fillet_obj(perimeter_obj, outside=True)
#
#     if subtract_fillet and perimeter_fillet:
#         delete_modifier(perimeter_fillet, modifier_name)
#         boolean = perimeter_fillet.modifiers.new(modifier_name, 'BOOLEAN')
#         boolean.operation = 'DIFFERENCE'
#         boolean.object = get_object_safely(subtract_fillet.name)
#
#         subtract_fillet.hide_set(True)
