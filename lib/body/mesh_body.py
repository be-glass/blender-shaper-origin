from . import Body
from ..fillet import Fillet
from ..helper.other import err_implementation
from ..shape.mesh_shape import MeshShape
from ..shape.perimeter import Perimeter


class MeshBody(Body):

    def setup(self):
        self.shape = self.shape_factory()
        self.shape.setup()
        self.obj = self.create_body_obj()
        self.collection.collect(self.obj, self.name)
        self.obj.display_type = 'WIRE'
        self.obj.soc_solid_name = self.name

    # private

    def create_body_obj(self):
        body = Fillet(self.shape).create(self.outside(), rounded=True)
        body.matrix_world = self.cut_obj.matrix_world
        return body

    def outside(self):
        return self.shape.is_exterior()

    def shape_factory(self):
        if self.cut_obj.soc_mesh_cut_type == 'Perimeter':
            shape = Perimeter
        elif self.cut_obj.soc_mesh_cut_type:
            shape = MeshShape
        else:
            err_implementation()
            shape = None
        return shape(self.cut_obj)

        def outside(self):
            return isinstance(self.shape, Perimeter)
