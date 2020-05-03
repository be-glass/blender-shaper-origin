from .__init__ import Body
from ..helper.curve import curve2mesh


class MeshedCurve(Body):

    def setup(self):  # possibly move to Body
        self.shape.setup()
        self.obj = curve2mesh(self.cut_obj, self.name)
        self.compartment.collect(self.obj, self.name, reset=False)
        self.obj.display_type = 'WIRE'
        self.obj.soc_solid_name = self.name

    def is_solid(self):
        return not self.shape.is_guide()

    # def update(self):
    #     pass

    # def clean(self):
    #     pass

    # private
