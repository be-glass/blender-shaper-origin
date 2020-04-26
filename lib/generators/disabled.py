from .base import Generator


class Disabled(Generator):

    def update(self):
        pass

    def setup(self):
        self.obj.display_type = 'TEXTURED'
        self.soc_object_type = 'None'
