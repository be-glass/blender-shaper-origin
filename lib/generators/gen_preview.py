from .base import Generator


class PreviewPerimeter(Generator):
    def transform(self):
        self.preview.transform_reference(self.obj)
        self.preview.transform_siblings(self.obj)
        self.preview.update_bounding_frame()


class PreviewMeshCut(Generator):
    pass


class PreviewCurveCut(Generator):
    pass
