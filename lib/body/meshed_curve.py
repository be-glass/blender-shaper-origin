from bpy.types import Object, BlendDataObjects

from .__init__ import Body
from ..helper.curve import curve2mesh, face_is_down
from ..helper.mesh_helper import shade_mesh_flat, repair_mesh
from ..helper.other import remove_object, delete_object, hide_objects


class MeshedCurve(Body):

    def setup(self) -> None:
        self.shape.setup()
        remove_object(self.name)
        self.obj = curve2mesh(self.cut_obj, self.name)
        # self.compartment.collect(self.obj, self.name, reset=False)
        self.obj.display_type = 'WIRE'
        self.obj.soc_solid_name = self.name

    def is_solid(self) -> bool:
        return not self.shape.is_guide()

    def update(self) -> None:
        sign = int(face_is_down(self.obj)) * 2 - 1

        for p in self.obj.data.splines[0].points:
            p.radius = 1.0

        bevel = self.get_bevel_object()
        bevel.scale = (sign * self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)
        self.obj.data.bevel_object = bevel
        solid_obj = self.update_mesh()
        self.obj.data.bevel_object = None
        self.obj.soc_solid_name = solid_obj.name

    # private

    def update_mesh(self) -> Object:
        delete_object(self.name)

        mesh_obj = curve2mesh(self.obj, self.name)
        mesh_obj.soc_object_type = 'Solid'

        self.compartment.link(mesh_obj)

        shade_mesh_flat(mesh_obj)
        repair_mesh(mesh_obj)  # TODO: needed?
        hide_objects(mesh_obj.name)

        return mesh_obj
