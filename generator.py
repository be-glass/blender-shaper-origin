import bpy
import math

from .constant import PREFIX
from .fillet import Fillet
from .helper.gen_helper import find_perimeters, cleanup, delete_modifiers, \
    find_siblings_by_type, cleanup_meshes, get_reference, delete_solid_objects, boolean_modifier_name, \
    delete_modifier, perimeter_thickness
from .helper.other import get_solid_collection, err_implementation, select_active, get_object_safely, length, \
    move_object, \
    delete_object, hide_objects, get_helper_collection
from .helper.mesh import repair_mesh, shade_mesh_flat, add_plane
from .helper.curve import add_nurbs_square
from .preview import Preview


def update(context, obj, reset=False, transform=False):
    active = context.object

    if reset:
        cleanup(context, obj)

    if obj.soc_curve_cut_type == 'None' and obj.soc_mesh_cut_type == 'None':
        obj.soc_object_type = "None"
        return
    if not obj.soc_simulate:
        return

    obj.soc_object_type = 'Cut'
    cut = get_generator(obj)
    generator = cut(context, obj)

    if reset:
        generator.setup()
    generator.update()
    select_active(context, active)


def transform(context, obj):
    cut = get_generator(obj)
    generator = cut(context, obj)
    generator.transform()


def update_hide_state(context, obj):
    cut = get_generator(obj)
    generator = cut(context, obj)
    generator.update_hide_state()


def get_generator(obj):
    if obj.soc_mesh_cut_type == 'Perimeter':
        cut = Perimeter
    elif obj.soc_curve_cut_type in ['Exterior', 'Interior', 'Online'] and obj.type == 'CURVE':
        cut = CurveCut
    elif obj.soc_mesh_cut_type in ['Cutout', 'Pocket'] and obj.type == 'MESH':
        cut = MeshCut
    else:
        err_implementation()
        return
    return cut


class Generator:

    def __init__(self, context, obj):
        self.obj = obj
        self.context = context
        self.solid_collection = get_solid_collection(context)

    def setup(self):
        self.obj.display_type = 'WIRE'

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
        for perimeter_obj in find_perimeters(collection):
            self.rebuild_boolean_modifier(perimeter_obj, self.obj)

    def reset_preview_object(self):
        name = self.obj.name + '.preview'
        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.object[name])

    def get_fillet_obj(self, obj=None, outside=False):
        if not obj:
            obj = self.obj
        fillet_obj = get_object_safely(obj.soc_solid_name, report_error=False)

        if not fillet_obj:
            fillet = Fillet(self.context, obj)
            fillet_obj = fillet.create(outside)

        return fillet_obj

    def rebuild_boolean_modifier(self, perimeter_obj, subtract_obj):

        modifier_name = boolean_modifier_name(subtract_obj)

        subtract_fillet = self.get_fillet_obj(subtract_obj)
        perimeter_fillet = self.get_fillet_obj(perimeter_obj, outside=True)

        delete_modifier(perimeter_fillet, modifier_name)
        boolean = perimeter_fillet.modifiers.new(modifier_name, 'BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = get_object_safely(subtract_fillet.name)

        subtract_fillet.hide_set(True)

    def update_hide_state(self):
        pass


class Perimeter(Generator):

    def setup(self):
        super().setup()

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
        solid = get_object_safely(self.obj.soc_solid_name)
        solid.hide_set(hidden)


class MeshCut(Generator):

    def setup(self):
        super().setup()

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


class CurveCut(Generator):

    def setup(self):
        super().setup()

        self.fillet = None

        bevel = self.get_bevel_object()
        move_object(bevel, self.solid_collection)
        self.obj.data.bevel_object = bevel

        self.obj.display_type = 'WIRE'
        modifier_name = PREFIX + 'Solidify'
        self.obj.modifiers.new(modifier_name, 'SOLIDIFY')

    def update(self):
        bevel = self.get_bevel_object()
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)

        mesh_obj = self.update_mesh()
        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection, mesh_obj)

    def get_bevel_object(self):
        if self.obj.soc_bevel_name:
            bevel_obj = get_object_safely(self.obj.soc_bevel_name)
            if bevel_obj:
                return bevel_obj

        collection = get_helper_collection(self.context)
        name = f'{PREFIX}{self.obj.name}.bevel'
        bevel_obj = add_nurbs_square(collection, name)
        bevel_obj.soc_object_type = 'Helper'
        self.obj.soc_bevel_name = bevel_obj.name

        return bevel_obj

    def update_mesh(self):
        mesh_name = PREFIX + self.obj.name + '.mesh'
        delete_object(mesh_name)
        solid_collection = get_solid_collection(self.context)

        # create a MESH version of the curve object
        depsgraph = self.context.evaluated_depsgraph_get()
        object_evaluated = self.obj.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(object_evaluated)
        mesh_obj = bpy.data.objects.new(mesh_name, mesh)
        mesh_obj.matrix_world = self.obj.matrix_world
        cleanup_meshes(self.context, self.obj, mesh_name)
        self.obj.users_collection[0].objects.link(mesh_obj)
        move_object(mesh_obj, solid_collection)
        shade_mesh_flat(mesh_obj)
        repair_mesh(self.context, mesh_obj)
        hide_objects(mesh_obj.name)

        return mesh_obj
