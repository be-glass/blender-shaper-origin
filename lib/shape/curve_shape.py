from . import Shape
from ..collection import Collection, Collect
from ..constant import PREFIX
from ..helper.curve import face_is_down, add_nurbs_square
from ..helper.gen_helper import cleanup_meshes
from ..helper.mesh_helper import curve2mesh, shade_mesh_flat, repair_mesh
from ..helper.other import get_object_safely, delete_object, hide_objects


def get_solid_collection():
    pass


class Curve(Shape):
    pass

    # def svg(self):
    #
    #     mesh_obj = curve2mesh(self.self.obj, add_face=True)
    #     proxy = Proxy(self.mesh_obj)
    #     proxy.setup_proxy(self.obj)
    #
    #     content = proxy.svg_mesh()
    #     attributes = svg_material_attributes(self.obj.soc_curve_cut_type)
    #     z = lift_z(self.self.obj)
    #
    #     return z, self.svg_object(content, attributes)

    def update(self):

        sign = int(face_is_down(self.obj)) * 2 - 1

        for p in self.obj.data.splines[0].points:
            p.radius = 1.0

        bevel = self.get_bevel_object()
        bevel.scale = (sign * self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)
        self.obj.data.bevel_object = bevel
        solid_obj = self.update_mesh()
        self.obj.data.bevel_object = None
        self.obj.soc_solid_name = solid_obj.name
        collections = self.obj.users_collection
        if collections:
            self.adjust_boolean_modifiers(collections[0])

    # private

    def update_mesh(self):
        mesh_name = PREFIX + self.obj.name + '.mesh'
        delete_object(mesh_name)

        cleanup_meshes(mesh_name)
        mesh_obj = curve2mesh(self.obj, mesh_name)
        get_solid_collection().objects.link(mesh_obj)

        shade_mesh_flat(mesh_obj)
        repair_mesh(mesh_obj)  # TODO: needed?
        hide_objects(mesh_obj.name)

        return mesh_obj

    def transform(self):
        solid_obj = get_object_safely(self.obj.soc_solid_name, report_error=False)
        if solid_obj:
            solid_obj.matrix_world = self.obj.matrix_world

    def get_bevel_object(self):
        if self.obj.soc_bevel_name:
            bevel_obj = get_object_safely(self.obj.soc_bevel_name, report_error=False)
            if bevel_obj:
                return bevel_obj

        collection = Collection(Collect.Helper)

        name = f'{PREFIX}{self.obj.name}.bevel'
        bevel_obj = add_nurbs_square(collection, name, self.obj.soc_curve_cut_type)
        bevel_obj.soc_object_type = 'Helper'
        bevel_obj.hide_set(True)
        self.obj.soc_bevel_name = bevel_obj.name

        return bevel_obj
