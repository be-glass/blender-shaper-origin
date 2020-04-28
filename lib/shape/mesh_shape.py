from . import Shape


class MeshShape(Shape):
    pass

# private

# if cut_type == 'Cutout':
#
#     thickness = perimeter_thickness(self.obj)
#     if thickness:
#         cutout_depth = thickness + self.length('1mm')
#     else:
#         cutout_depth = self.length('1cm')
#
#     if not math.isclose(self.obj.soc_cut_depth, cutout_depth, abs_tol=self.length('0.01mm')):
#         self.obj.soc_cut_depth = cutout_depth
#         return
#
#     delta = 0.0
# elif cut_type == 'Pocket':
#     delta = self.length('0.1mm')
# else:
#     delta = 0.0
#
# self.adjust_solidify_thickness(delta=delta)

# def transform(self):
#     fillet_obj = self.get_fillet_obj()
#     fillet_obj.matrix_world = self.obj.matrix_world
#
# def svg(self):
#
#     fillet = Fillet(self.self.obj)
#     fillet_obj = fillet.create()
#     proxy = Proxy(self.fillet_obj)
#     proxy.setup_proxy(self.obj)
#
#     content = proxy.svg_mesh()
#     attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
#     contents = self.svg_object(content, attributes)
#     z = lift_z(self.self.obj)
#
#     return z, contents
