from . import Body
from ..helper.other import err_implementation
from ..shape.curve_shape import Curve


class MeshedCurve(Body):

    def setup(self):  # possibly move to Body
        self.shape = self.shape_factory()
        self.shape.setup()
        self.obj = self.create_body_obj()
        self.collection.collect(self.obj, self.name)
        self.obj.display_type = 'WIRE'
        self.obj.soc_solid_name = self.name

    def update(self):
        pass

    def clean(self):
        pass

    # private

    def create_body_obj(self):
        # TODO
        pass

    def shape_factory(self):
        if self.obj.soc_cuve_cut_type:
            shape = Curve
        else:
            err_implementation()
            shape = None
        return shape(self.obj)
