from ..fillet import Fillet
from ..helper.gen_helper import *
from ..helper.other import get_solid_collection, get_object_safely, length, \
    vector2string, err_implementation
from ..helper.preview_helper import transform_export
from ..preview import Preview


class Generator:

    def __init__(self, context, obj):
        self.context = context
        self.obj = obj
        self.perimeter = None
        self.soc_object_type = 'None'
        self.preview = Preview(context)

    def reset(self):
        cleanup(self.context, self.obj)
        self.setup()
        self.update()

    def setup(self):
        self.solid_collection = get_solid_collection(self.context)
        self.obj.display_type = 'WIRE'
        self.obj.soc_known_as = self.obj.name

    def cleanup(self):
        delete_modifiers(self.obj)
        delete_solid_objects(self.context, self.obj)


    def transform_preview(self, matrix):
        name = self.obj.soc_preview_name
        if name:
            preview = get_object_safely(name)
            preview.matrix_world = matrix

    def adjust_solidify_thickness(self, delta=0.0):
        master = self.obj
        revision = self.get_fillet_obj()

        modifier_name = PREFIX + 'Solidify'
        if modifier_name in revision.modifiers:
            revision.modifiers[modifier_name].thickness = master.soc_cut_depth + delta

    def length(self, quantity_with_unit):
        return length(self.context, quantity_with_unit)

    def adjust_boolean_modifiers(self, collection):
        solid_obj = get_object_safely(self.obj.soc_solid_name)
        for perimeter_obj in find_perimeters(collection):
            self.rebuild_boolean_modifier(perimeter_obj, solid_obj)

    def reset_preview_object(self):
        name = self.obj.name + '.preview'
        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.object[name])

    def get_fillet_obj(self, obj=None, outside=False):
        if not obj:
            obj = self.obj
        fillet_obj = get_object_safely(obj.soc_solid_name, report_error=False)

        if obj.soc_mesh_cut_type == 'None':
            return None

        if not fillet_obj:
            fillet = Fillet(self.context, obj)
            fillet_obj = fillet.create(outside)

        return fillet_obj

    def rebuild_boolean_modifier(self, perimeter_obj, subtract_obj):

        modifier_name = boolean_modifier_name(subtract_obj)

        subtract_fillet = self.get_fillet_obj(subtract_obj)
        perimeter_fillet = self.get_fillet_obj(perimeter_obj, outside=True)

        if subtract_fillet and perimeter_fillet:
            delete_modifier(perimeter_fillet, modifier_name)
            boolean = perimeter_fillet.modifiers.new(modifier_name, 'BOOLEAN')
            boolean.operation = 'DIFFERENCE'
            boolean.object = get_object_safely(subtract_fillet.name)

            subtract_fillet.hide_set(True)

    def update_hide_state(self):
        pass

    def svg_object(self, content, attributes):
        return \
            f'<g id="{self.obj.name_full}" class="{self.obj.type}" {attributes}>' + \
            ''.join(content) + \
            '</g>'

    def svg_polygon(self, polygon):
        points = [self.obj.data.vertices[i] for i in polygon.vertices]
        return self.svg_path(points, is_closed=True)

    def svg_path(self, points, is_closed):
        source = ''
        path_cmd = 'M'
        for point in points:
            vector = transform_export(self.context, self.obj, self.perimeter) @ point.co
            source += path_cmd + vector2string(vector)
            path_cmd = 'L'
        if is_closed:
            source += 'Z'
        return f'<path d="{source}"/>'

    def svg_mesh(self):

        content = ''
        for polygon in self.obj.data.polygons:
            c = self.svg_polygon(polygon)
            content += c

        return content
