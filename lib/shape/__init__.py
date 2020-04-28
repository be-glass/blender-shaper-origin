class Shape:
    def __init__(self, obj):
        self.obj = obj
        self.obj.display_type = 'WIRE'
        self.obj.soc_known_as = self.obj.name

    def setup(self):
        pass

    def update(self):
        pass

    def clean(self):
        pass

    ### private

    def is_exterior(self):
        return False

    def is_perimeter(self):
        return False

    def is_guide(self):
        return False
