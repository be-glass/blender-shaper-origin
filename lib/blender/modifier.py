class Modifier:
    def __init__(self, obj) -> None:
        self.mod = obj.modifiers

    def subtract(self, subtrahend, name) -> None:
        self.remove(name)
        boolean = self.mod.new(name, 'BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = subtrahend

    def remove(self, name) -> None:
        for m in self.mod:
            if m.name == name:
                self.mod.remove(m)

    def exists(self, name) -> bool:
        return bool(name in [m.name for m in self.mod])

    def set_thickness(self, name, thickness) -> None:
        solidify = [m for m in self.mod if m.type == 'SOLIDIFY']
        if solidify:
            solidify[0].thickness = thickness
