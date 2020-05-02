from .__init__ import Body


class MeshedCurve(Body):

    def setup(self):  # possibly move to Body
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

