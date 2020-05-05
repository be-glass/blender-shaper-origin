from bpy.types import Object

from .__init__ import Body
from ..blender.compartment import Compartment
from ..blender.fillet import Fillet
from ..helper.other import length


class MeshBody(Body):

    def setup(self) -> None:
        self.shape.setup()

        if not self.shape.is_guide():
            self.obj = self.create_body_obj()
            self.compartment.collect(self.obj, self.name)

            if self.shape.is_perimeter():
                self.obj.display_type = 'TEXTURED'
            else:
                self.obj.display_type = 'WIRE'
                if Compartment.by_obj(self.cut_obj).perimeter_objs():
                    self.obj.hide_set(True)
                else:
                    self.obj.hide_set(False)
            self.obj.hide_select = True

    def is_solid(self) -> bool:
        return not self.shape.is_guide()

    # private

    def create_body_obj(self) -> Object:
        body = Fillet(self.shape.obj).create(self.shape.is_exterior(), rounded=True)
        body.matrix_world = self.cut_obj.matrix_world
        body.soc_object_type = 'Body'
        return body

    def outside(self) -> bool:
        return self.shape.is_exterior()

    def thickness_delta(self) -> float:
        if self.cut_obj.soc_mesh_cut_type == 'Cutout':
            return 0.2
        else:
            return 0.0
