from ..body import Body
from ..blender.compartment import Compartment, Collect
from ..constant import PREFIX
from ..blender.modifier import Modifier


class Solid:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj
        self.defaults()

        self.mod_solidify_name = PREFIX + 'Solidify'
        self.mod_boolean_name = PREFIX + 'Boolean.' + self.cut_obj.name
        self.body = Body.factory(cut_obj)

    def defaults(self):
        self.solidify_name = None
        self.body = None

    def setup(self):
        # self.compartment = Compartment.by_enum(Collect.Solid)

        self.body.setup()

        if self.body.is_solid():
            self.solidify()
            self.subtract_from_perimeter()

    def update(self):
        self.body.update()
        if self.cut_obj.type == 'MESH':
            self.set_thickness()

    def clean(self):
        self.body.clean()
        self.defaults()

    def transform(self):
        if self.cut_obj:
            matrix = self.cut_obj.matrix_world
            self.body.transform(matrix)

    def subtract(self, other_body, modifier_name):
        minuend = self.body.get()
        subtrahend = other_body.get()
        if minuend and subtrahend:
            Modifier(minuend).subtract(subtrahend, modifier_name)

            # subtrahend.hide_set(True)   # TODO: activate later

    # private

    def subtract_from_perimeter(self):
        if self.body.shape:
            if self.body.shape.is_perimeter():
                subtrahend_objs = Compartment.by_obj(self.cut_obj).subtrahend_objs()
                for s_obj in subtrahend_objs:
                    solid = Solid(s_obj)
                    self.subtract(solid.body, solid.mod_boolean_name)

            else:
                perimeter_objs = Compartment.by_obj(obj=self.cut_obj).perimeter_objs()
                if perimeter_objs:
                    Solid(perimeter_objs[0]).subtract(self.body, self.mod_boolean_name)

    def solidify(self):
        self.body.obj.modifiers.new(self.mod_solidify_name, 'SOLIDIFY')

    def set_thickness(self):
        body_obj = self.body.get()
        if body_obj:
            Modifier(body_obj).set_thickness(self.mod_solidify_name,
                                             self.cut_obj.soc_cut_depth + self.body.thickness_delta())
