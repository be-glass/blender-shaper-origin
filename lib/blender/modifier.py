class Modifier:
    def __init__(self, obj):
        self.mod = obj.modifiers

    def subtract(self, subtrahend, name):
        self.remove(name)
        boolean = self.mod.new(name, 'BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = subtrahend

    def remove(self, name):
        for m in self.mod:
            if m.name == name:
                self.mod.remove(m)

    def exists(self, name):
        return bool(name in [m.name for m in self.mod])

    def set_thickness(self, name, thickness):
        solidify = [m for m in self.mod if m.type == 'SOLIDIFY']
        if solidify:
            solidify[0].thickness = thickness

#     def delete_modifier(obj, name):
#         if name in obj.modifiers.keys():
#             obj.modifiers.remove(obj.modifiers[name])
#
#     def delete_modifiers(obj):
#         for modifier in obj.modifiers:
#             if modifier.name.startswith(PREFIX):
#                 obj.modifiers.remove(modifier)
#
#
# def boolean_modifier_name(cut_obj):
#     return PREFIX + "Boolean." + cut_obj.name
#
#
# def cleanup_boolean_modifiers(target_obj):
#     solid_obj = get_object_safely(target_obj.soc_solid_name, report_error=False)
#
#     if solid_obj:
#         collection = target_obj.users_collection[0]
#         for perimeter in find_perimeters(collection):
#             delete_modifier(perimeter, boolean_modifier_name(solid_obj))
