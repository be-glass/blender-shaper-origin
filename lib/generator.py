import math

from .fillet import Fillet
from .helper.curve import add_nurbs_square, face_is_down
from .helper.gen_helper import *
from .helper.mesh import repair_mesh, shade_mesh_flat, curve2mesh
from .helper.other import get_solid_collection, get_object_safely, length, \
    delete_object, hide_objects, get_helper_collection, find_first_perimeter, vector2string
from .helper.preview_helper import transform_export
from .helper.svg import svg_material_attributes
from .preview import Preview


class Generator:

    def __init__(self, context, obj=None):
        self.context = context
        self.obj = obj
        self.perimeter = None
        self.soc_object_type = 'None'

    def create(self, obj):
        self.obj = obj

        ot = obj.soc_object_type

        if not obj.soc_simulate:
            cut = Disabled
        if self.obj.soc_mesh_cut_type == 'None' and self.obj.soc_curve_cut_type == 'None':
            cut = Disabled
        elif ot in ['None', 'Cut']:
            if self.obj.soc_mesh_cut_type == 'Perimeter':
                cut = Perimeter
            elif self.obj.soc_curve_cut_type in ['Exterior', 'Interior', 'Online'] and self.obj.type == 'CURVE':
                cut = CurveCut
            elif self.obj.soc_mesh_cut_type in ['Cutout', 'Pocket'] and self.obj.type == 'MESH':
                cut = MeshCut
            else:
                cut = Disabled
        elif ot == 'Proxy':
            cut = Proxy
        else:
            cut = Disabled
        return cut(self.context, self.obj)

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

    def transform(self):
        fillet_obj = self.get_fillet_obj()
        fillet_obj.matrix_world = self.obj.matrix_world

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
        z = 0
        for point in points:
            vector = transform_export(self.context, self.obj, self.perimeter) @ point.co
            source += path_cmd + vector2string(vector)
            path_cmd = 'L'
            z = vector[2]
        if is_closed:
            source += 'Z'
        return f'<path d="{source}"/>', z

    def svg_mesh(self):

        z = 0
        content = ''
        for polygon in self.obj.data.polygons:
            c, z = self.svg_polygon(polygon)
            content += c

        return content, z


class Disabled(Generator):

    def update(self):
        pass

    def setup(self):
        self.obj.display_type = 'TEXTURED'
        self.soc_object_type = 'None'


class Perimeter(Generator):

    def setup(self):
        super().setup()

        self.obj.soc_object_type = 'Cut'

        self.fillet = Fillet(self.context, self.obj)
        self.fillet.create(outside=True)
        self.fillet.display_type = 'WIRE'

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.get_fillet_obj()
        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        types = ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']
        for cut_obj in find_siblings_by_type(types, sibling=self.obj):
            self.rebuild_boolean_modifier(self.obj, cut_obj)

        self.reference = get_reference(self.context, self.obj)

        if self.context.scene.so_cut.preview:
            Preview(self.context).add_object(self.obj, self.obj)

    def update(self):

        self.adjust_solidify_thickness()

        cutouts = find_siblings_by_type('Cutout', sibling=self.context.object)
        for cut in cutouts:
            cut.soc_cut_depth = self.obj.soc_cut_depth + self.length('1mm')

    def update_hide_state(self):
        hidden = self.obj.hide_get()  # or self.obj.users_collection[0].hide_viewport   # collection cannot work
        solid = get_object_safely(self.obj.soc_solid_name, report_error=False)
        if solid:
            solid.hide_set(hidden)

    def svg(self):
        # self.perimeter = self.obj

        fillet = Fillet(self.context, self.obj)
        fillet_obj = fillet.create(outside=True)
        proxy = Proxy(self.context, fillet_obj)
        proxy.setup_proxy(self.obj)

        content, z = self.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)

        return z, self.svg_object(content, attributes)


class MeshCut(Generator):

    def setup(self):
        super().setup()
        self.obj.soc_object_type = 'Cut'

        self.fillet = Fillet(self.context, self.obj)
        self.fillet.create()
        self.fillet.display_type = 'WIRE'

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.get_fillet_obj()

        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection)

    def update(self):

        cut_type = self.obj.soc_mesh_cut_type

        if cut_type == 'Cutout':

            thickness = perimeter_thickness(self.obj)
            if thickness:
                cutout_depth = thickness + self.length('1mm')
            else:
                cutout_depth = self.length('1cm')

            if not math.isclose(self.obj.soc_cut_depth, cutout_depth, abs_tol=self.length('0.01mm')):
                self.obj.soc_cut_depth = cutout_depth
                return

            delta = 0.0
        elif cut_type == 'Pocket':
            delta = self.length('0.1mm')
        else:
            delta = 0.0

        self.adjust_solidify_thickness(delta=delta)

    def svg(self):

        fillet = Fillet(self.context, self.obj)
        fillet_obj = fillet.create(outside=True)
        proxy = Proxy(self.context, fillet_obj)
        proxy.setup_proxy(self.obj)

        content, z = proxy.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_mesh_cut_type)

        return z, self.svg_object(content, attributes)


class Proxy(Generator):

    def setup_proxy(self, source_obj):
        reference = get_reference(self.context, source_obj)
        self.obj.soc_reference_name = reference.name
        self.perimeter = find_first_perimeter(source_obj)
        self.obj.soc_object_type = 'Proxy'


class CurveCut(Generator):

    def svg(self):

        mesh_obj = curve2mesh(self.context, self.obj, add_face=True)
        proxy = Proxy(self.context, mesh_obj)
        proxy.setup_proxy(self.obj)

        content, z = proxy.svg_mesh()
        attributes = svg_material_attributes(self.obj.soc_curve_cut_type)

        return z, self.svg_object(content, attributes)

    def setup(self):
        super().setup()

        self.obj.soc_object_type = 'Cut'
        self.fillet = None
        self.obj.display_type = 'WIRE'

    def update(self):

        sign = int(face_is_down(self.context, self.obj)) * 2 - 1

        for p in self.obj.data.splines[0].points:
            p.radius = 1.0

        bevel = self.get_bevel_object()
        bevel.scale = (sign * self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)
        self.obj.data.bevel_object = bevel
        solid_obj = self.update_mesh()
        self.obj.data.bevel_object = None
        self.obj.soc_solid_name = solid_obj.name
        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection)

    def get_bevel_object(self):
        if self.obj.soc_bevel_name:
            bevel_obj = get_object_safely(self.obj.soc_bevel_name)
            if bevel_obj:
                return bevel_obj

        collection = get_helper_collection(self.context)
        name = f'{PREFIX}{self.obj.name}.bevel'
        bevel_obj = add_nurbs_square(collection, name, self.obj.soc_curve_cut_type)
        bevel_obj.soc_object_type = 'Helper'
        bevel_obj.hide_set(True)
        self.obj.soc_bevel_name = bevel_obj.name

        return bevel_obj

    def update_mesh(self):
        mesh_name = PREFIX + self.obj.name + '.mesh'
        delete_object(mesh_name)

        cleanup_meshes(self.context, mesh_name)
        mesh_obj = curve2mesh(self.context, self.obj, mesh_name)
        get_solid_collection(self.context).objects.link(mesh_obj)

        shade_mesh_flat(mesh_obj)
        repair_mesh(self.context, mesh_obj)  # TODO: needed?
        hide_objects(mesh_obj.name)

        return mesh_obj
