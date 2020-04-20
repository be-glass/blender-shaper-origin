import bpy, math

from . import helper, gen_helper
from .gen_helper import find_perimeters, rebuild_boolean_modifier, cleanup, delete_modifiers, \
    delete_internal_objects, find_siblings_by_type, cleanup_meshes, get_reference
from .helper import get_internal_collection
from .preview import Preview

from .fillet import Fillet
from .constant import PREFIX


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
    helper.select_active(context, active)


def get_generator(obj):
    if obj.soc_mesh_cut_type == 'Perimeter':
        cut = Perimeter
    elif obj.soc_curve_cut_type in ['Exterior', 'Interior', 'Online'] and obj.type == 'CURVE':
        cut = CurveCut
    elif obj.soc_mesh_cut_type in ['Cutout', 'Pocket'] and obj.type == 'MESH':
        cut = MeshCut
    else:
        helper.err_implementation()
        return
    return cut


def transform(context, obj):
    cut = get_generator(obj)
    generator = cut(context, obj)
    generator.transform()


def transform_previews(context, frame_obj):
    for obj in bpy.data.objects:
        if obj.soc_object_type == 'Cut':
            reference = gen_helper.get_reference(obj)
            # reference = helper.get_object_safely(obj.soc_reference_name)

            transform = frame_obj.matrix_world @ reference.matrix_world

            cut = get_generator(obj)
            generator = cut(context, obj)
            generator.transform_preview(transform)


class Generator:

    def __init__(self, context, obj):
        self.obj = obj
        self.context = context
        self.internal_collection = get_internal_collection(self.obj)
        self.fillet = Fillet(obj)

    def setup(self):
        self.obj.display_type = 'WIRE'
        if self.fillet:
            self.fillet.display_type = 'WIRE'

    def cleanup(self):
        delete_modifiers(self.obj)
        delete_internal_objects(self.obj)

    def transform(self):
        fillet_obj = self.fillet.get_obj()
        fillet_obj.matrix_world = self.obj.matrix_world

    def transform_preview(self, matrix):
        name = self.obj.soc_preview_name
        if name:
            preview = helper.get_object_safely(name)
            preview.matrix_world = matrix

    def adjust_solidify_thickness(self, delta=0.0):
        master = self.obj
        revision = self.fillet.get_obj()

        modifier_name = PREFIX + 'Solidify'
        if modifier_name in revision.modifiers:
            revision.modifiers[modifier_name].thickness = master.soc_cut_depth + delta

    def length(self, quantity_with_unit):
        return helper.length(self.context, quantity_with_unit)

    def adjust_boolean_modifiers(self, collection):
        for perimeter_obj in find_perimeters(collection):
            rebuild_boolean_modifier(perimeter_obj, self.obj)

    def reset_preview_object(self):
        name = self.obj.name+'.preview'
        if name in bpy.data.objects.keys():
            bpy.data.objects.remove(bpy.data.object[name])


class Perimeter(Generator):

    def setup(self):
        super().setup()

        self.fillet.create(outside=True)

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.fillet.get_obj()
        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        types = ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']
        for cut in find_siblings_by_type(types, sibling=self.obj):
            rebuild_boolean_modifier(self.obj, cut)

        self.reference = get_reference(self.obj)

        if self.context.scene.so_cut.preview:
            Preview(self.context).add_object(self.obj)

    def update(self):
        self.adjust_solidify_thickness()

        cutouts = find_siblings_by_type('Cutout', sibling=self.context.object)
        for cut in cutouts:
            cut.soc_cut_depth = self.obj.soc_cut_depth + self.length('1mm')


class MeshCut(Generator):

    def setup(self):
        super().setup()

        self.fillet.create()

        modifier_name = PREFIX + 'Solidify'
        fillet_obj = self.fillet.get_obj()

        fillet_obj.modifiers.new(modifier_name, 'SOLIDIFY')

        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection)

    def update(self):

        cut_type = self.obj.soc_mesh_cut_type

        if cut_type == 'Cutout':

            perimeter_thickness = gen_helper.perimeter_thickness(self.obj)
            if perimeter_thickness:
                cutout_depth = perimeter_thickness + self.length('1mm')
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

        bevel = self.create_bevel_object()
        helper.move_object(bevel, self.internal_collection)
        self.obj.data.bevel_object = bevel

        self.obj.display_type = 'WIRE'
        modifier_name = PREFIX + 'Solidify'
        self.obj.modifiers.new(modifier_name, 'SOLIDIFY')

    def update(self):
        bevel = helper.get_object_safely(f'{PREFIX}{self.obj.name}.bevel')
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)

        mesh_obj = self.update_mesh()
        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection, mesh_obj)

    def create_bevel_object(self):
        name = f'{PREFIX}{self.obj.name}.bevel'

        # normalize curve radii
        helper.apply_scale(self.context, self.obj)
        for spline in self.obj.data.splines:
            for p in spline.bezier_points:
                p.radius = 1.0

        # create new one
        bevel = helper.add_plane(self.context, name, 1.0)

        # move object origin to upper edge
        bevel.location = (0, -0.5, 0)
        helper.apply_scale(self.context, self.obj)

        # scale
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)

        bpy.ops.object.convert(target='CURVE')

        return bevel

    def update_mesh(self):
        mesh_name = PREFIX + self.obj.name + '.mesh'
        helper.delete_object(mesh_name)
        internal_collection = get_internal_collection(self.obj)

        # create a MESH version of the curve object
        depsgraph = self.context.evaluated_depsgraph_get()
        object_evaluated = self.obj.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(object_evaluated)
        mesh_obj = bpy.data.objects.new(mesh_name, mesh)
        mesh_obj.matrix_world = self.obj.matrix_world
        cleanup_meshes(self.obj, mesh_name)
        self.obj.users_collection[0].objects.link(mesh_obj)
        helper.move_object(mesh_obj, internal_collection)
        helper.shade_mesh_flat(mesh_obj)
        helper.repair_mesh(self.context, mesh_obj)
        helper.hide_objects(mesh_obj.name)

        return mesh_obj
