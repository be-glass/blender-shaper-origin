class Shape:
    def __init__(self, context, obj):
        self.context = context
        self.obj = obj
        self.obj.display_type = 'WIRE'
        self.obj.soc_known_as = self.obj.name
