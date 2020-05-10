from .__init__ import Shape


class MeshGuide(Shape):


    def is_guide(self) -> bool:
        return True

    # def svg(self):
    #     content = self.svg_mesh()
    #     attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
    #     contents = self.svg_object(content, attributes)
    #     z = lift_z(self.self.obj)
    #
    #     return z, contents
