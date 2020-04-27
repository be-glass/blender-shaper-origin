class MeshGuide(Generator):

    def setup(self):
        super().setup()
        self.obj.soc_object_type = 'Cut'

    def update(self):
        pass

    def transform(self):
        pass

    def svg(self):
        content = self.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)
        contents = self.svg_object(content, attributes)
        z = lift_z(self.context, self.obj)

        return z, contents
