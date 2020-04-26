from .base import Generator


class Bounding(Generator):
    def transform(self):
        self.preview.transform_previews(self.context, self.obj)

    def setup(self):
        pass

    def update(self):
        pass
