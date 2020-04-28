from ..collection import Collection, Collect
from ..constant import PREFIX
from ..shape import Shape


class Body:

    def __init__(self, cut_obj):
        self.cut_obj = cut_obj
        self.defaults()

        # config
        self.cut_obj.display_type = 'WIRE'
        self.cut_obj.soc_known_as = self.cut_obj.name
        self.name = PREFIX + self.cut_obj.name + ".body"
        self.collection = Collection(Collect.Solid)

    def defaults(self):
        self.shape = None

    def clean(self):
        self.collection.remove(self.name)
        Shape(self.cut_obj).clean()

    def update(self):
        self.shape.update()
