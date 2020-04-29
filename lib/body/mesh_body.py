from . import Body
from ..collection import Collection
from ..fillet import Fillet
from ..helper.other import length


class MeshBody(Body):

    def setup(self):
        self.shape.setup()

        if not self.shape.is_guide():
            self.obj = self.create_body_obj()
            self.collection.collect(self.obj, self.name)

            if self.shape.is_perimeter():
                self.obj.display_type = 'TEXTURED'
            else:
                self.obj.display_type = 'WIRE'
                if Collection.by_obj(self.cut_obj).perimeter_objs():
                    self.obj.hide_set(True)
                else:
                    self.obj.hide_set(False)
            self.obj.hide_select = True

    def is_solid(self):
        return not self.shape.is_guide()

    # private

    def create_body_obj(self):
        body = Fillet(self.shape).create(self.shape.is_exterior(), rounded=True)
        body.matrix_world = self.cut_obj.matrix_world
        return body

    def outside(self):
        return self.shape.is_exterior()

    def thickness_delta(self):
        if self.cut_obj.soc_mesh_cut_type == 'Cutout':
            return length('1 mm')
        else:
            return length('0.1 mm')
