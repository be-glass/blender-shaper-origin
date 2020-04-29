from ..body import Body
from ..body.mesh_body import MeshBody
from ..body.meshed_curve import MeshedCurve
from ..collection import Collection, Collect
from ..constant import PREFIX
from ..helper.other import err_implementation
from ..modifier import Modifier


class Solid:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj
        self.defaults()

        # config
        self.mod_solidify_name = PREFIX + 'Solidify'
        self.mod_boolean_name = PREFIX + 'Boolean.' + self.cut_obj.name

    def defaults(self):
        self.solidify_name = None
        self.body = None

    def setup(self):
        self.collection = Collection.by_enum(Collect.Solid)

        # build
        self.body = self.body_factory()
        self.body.setup()

        if self.body and self.body.is_solid():
            self.solidify()
            self.subtract_from_perimeter()

    def update(self):
        body = self.body_factory()
        if body:
            body.update()
            self.set_thickness()

    def clean(self):
        Body(self.cut_obj).clean()
        self.defaults()

    def transform(self):
        if self.cut_obj:
            matrix = self.cut_obj.matrix_world
            Body(self.cut_obj).transform(matrix)

    def subtract(self, body, modifier_name):
        b = self.body_factory()
        minuend = b.get()
        subtrahend = body.get()
        if minuend and subtrahend:
            Modifier(minuend).subtract(subtrahend, modifier_name)

            # subtrahend.hide_set(True)   # TODO: activate later

    # private

    def subtract_from_perimeter(self):
        if self.body.shape:
            if self.body.shape.is_perimeter():
                subtrahend_objs = Collection.by_obj(self.cut_obj).subtrahend_objs()
                for s_obj in subtrahend_objs:
                    solid = Solid(s_obj)
                    body = solid.body_factory()
                    if body:
                        self.subtract(body, solid.mod_boolean_name)

            else:
                perimeter_objs = Collection.by_obj(obj=self.cut_obj).perimeter_objs()
                if perimeter_objs:
                    Solid(perimeter_objs[0]).subtract(self.body, self.mod_boolean_name)

    def solidify(self):
        self.body.obj.modifiers.new(self.mod_solidify_name, 'SOLIDIFY')

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
        body = self.body_factory().get()
        if body:
            Modifier(body).set_thickness(self.mod_solidify_name, self.cut_obj.soc_cut_depth + delta)

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
