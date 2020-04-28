from . import Body
from ..fillet import Fillet
from ..helper.other import err_implementation
from ..shape.mesh_guide import MeshGuide
from ..shape.mesh_shape import MeshShape
from ..shape.perimeter import Perimeter


class MeshBody(Body):

    def setup(self):
        self.shape = self.shape_factory()
        self.shape.setup()

        if not self.shape.is_guide():
            self.obj = self.create_body_obj()
            self.collection.collect(self.obj, self.name)

            if self.shape.is_perimeter():
                self.obj.display_type = 'TEXTURED'
            else:
                self.obj.display_type = 'WIRE'

    def is_solid(self):
        return not self.shape.is_guide()

    # private

    def create_body_obj(self):
        body = Fillet(self.shape).create(self.shape.is_exterior(), rounded=True)
        body.matrix_world = self.cut_obj.matrix_world
        return body

    def outside(self):
        return self.shape.is_exterior()

    def shape_factory(self):
        if self.cut_obj.soc_mesh_cut_type == 'Perimeter':
            shape = Perimeter
        elif self.cut_obj.soc_mesh_cut_type == 'GuideArea':
            shape = MeshGuide
        elif self.cut_obj.soc_mesh_cut_type:
            shape = MeshShape
        else:
            err_implementation()
            shape = None
        return shape(self.cut_obj)

