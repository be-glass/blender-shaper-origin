import bpy, math

from . import helper, sim_helper
from .sim_helper import find_perimeters, rebuild_boolean_modifier, cleanup, get_internal_collection, delete_modifiers, \
    delete_internal_objects, find_siblings_by_type, cleanup_meshes

from .fillet import Fillet
from .constant import Prefix


def update(context, obj, reset=False, dogbone_obj=None):
    active = context.object

    cleanup(context, obj)

    if not obj.soc_simulate:
        return
    if obj.soc_curve_cut_type == 'None' and obj.soc_mesh_cut_type == 'None':
        return

    if obj.soc_mesh_cut_type == 'Perimeter':
        cut = Perimeter
    elif obj.soc_curve_cut_type in ['Exterior', 'Interior', 'Online'] and obj.type == 'CURVE':
        cut = CurveCut
    elif obj.soc_mesh_cut_type in ['Cutout', 'Pocket'] and obj.type == 'MESH':
        cut = MeshCut
    else:
        helper.err_implementation()
        return

    generator = cut(context, obj)

    if reset:
        generator.setup()

    generator.update()
    helper.select_active(context, active)


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

    def adjust_solidify_thickness(self, delta=0.0):
        master = self.obj
        revision = self.fillet.get_obj()

        modifier_name = Prefix + 'Solidify'
        if modifier_name in revision.modifiers:
            revision.modifiers[modifier_name].thickness = master.soc_cut_depth + delta

    def length(self, quantity_with_unit):
        return helper.length(self.context, quantity_with_unit)

    def adjust_boolean_modifiers(self, collection):
        for perimeter_obj in find_perimeters(collection):
            rebuild_boolean_modifier(perimeter_obj, self.obj, self.fillet)


class Perimeter(Generator):

    def setup(self):
        super().setup()

        self.fillet.create(outside=True)


        # self.obj.display_type = 'WIRE'

        modifier_name = Prefix + 'Solidify'
        revision = self.fillet.get_obj()
        revision.modifiers.new(modifier_name, 'SOLIDIFY')

        types = ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']
        for cut in find_siblings_by_type(types, sibling=self.obj):
            cut_filleted = Fillet(cut).get_obj()
            rebuild_boolean_modifier(self.obj, cut_filleted)

    def update(self):
        self.adjust_solidify_thickness()

        cutouts = find_siblings_by_type('Cutout', sibling=self.context.object)
        for cut in cutouts:
            cut.soc_cut_depth = self.obj.soc_cut_depth + self.length('1mm')


class MeshCut(Generator):

    def setup(self):
        super().setup()

        self.fillet.create()

        modifier_name = Prefix + 'Solidify'
        revision = self.fillet.get_obj()
        revision.modifiers.new(modifier_name, 'SOLIDIFY')


        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection)

    def update(self):

        cut_type = self.obj.soc_mesh_cut_type

        if cut_type == 'Cutout':

            perimeter_thickness = sim_helper.perimeter_thickness(self.obj)
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
        modifier_name = Prefix + 'Solidify'
        self.obj.modifiers.new(modifier_name, 'SOLIDIFY')

    def update(self):
        bevel = helper.get_object_safely(f'{Prefix}{self.obj.name}.bevel')
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)

        mesh_obj = self.update_mesh()
        collection = self.obj.users_collection[0]
        self.adjust_boolean_modifiers(collection, mesh_obj)

    def create_bevel_object(self):
        name = f'{Prefix}{self.obj.name}.bevel'

        # normalize curve radii
        helper.apply_scale()
        for spline in self.obj.data.splines:
            for p in spline.bezier_points:
                p.radius = 1.0

        # create new one
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        bevel = self.context.active_object
        bevel.name = name

        # move object origin to upper edge
        bevel.location = (0, -0.5, 0)
        helper.apply_transformations()

        # scale
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)

        # delete first face
        bpy.ops.object.mode_set(mode='EDIT')
        bevel.data.polygons[0].select = True
        bpy.ops.mesh.delete(type='ONLY_FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='CURVE')

        return bevel

    def update_mesh(self):
        mesh_name = Prefix + self.obj.name + '.mesh'
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



