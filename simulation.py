import bpy

from . import constant, helper, sim_helper


def update(context, obj, reset=False):
    active = context.object

    if (not obj.soc_simulate) or (obj.soc_cut_type == 'None'):
        sim_helper.cleanup(context, obj)
        return

    if obj.soc_cut_type == 'Perimeter':
        cut = Perimeter
    elif obj.soc_cut_type in ['Exterior', 'Interior', 'Online'] and obj.type == 'CURVE':
        cut = CurveCut
    elif obj.soc_cut_type in ['Cutout', 'Pocket'] and obj.type == 'MESH':
        cut = MeshCut
    else:
        helper.err_implementation()
        return

    simulation = cut(context, obj)

    if reset:
        simulation.setup()

    simulation.update()
    helper.select_active(context, active)


class Simulation:

    def __init__(self, context, obj):
        self.obj = obj
        self.context = context
        self.internal_collection = sim_helper.get_internal_collection(constant.prefix + 'internal', self.obj)

    def cleanup(self):
        sim_helper.delete_modifiers(self.obj)
        sim_helper.delete_internal_objects(self.obj)

    def adjust_solidify_thickness(self, delta=0.0):
        modifier_name = constant.prefix + 'Solidify'
        if modifier_name in self.obj.modifiers:
            self.obj.modifiers[modifier_name].thickness = self.obj.soc_cut_depth + delta


class Perimeter(Simulation):

    def setup(self):
        self.cleanup()
        modifier_name = constant.prefix + 'Solidify'
        self.obj.modifiers.new(modifier_name, 'SOLIDIFY')

        for cut in sim_helper.find_siblings_by_type(self.obj, ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']):
            sim_helper.rebuild_boolean_modifier(self.obj, cut)

    def update(self):
        self.adjust_solidify_thickness()

        cutouts = sim_helper.find_siblings_by_type(self.context.object, 'Cutout')
        for cut in cutouts:
            cut.soc_cut_depth = self.obj.soc_cut_depth + helper.length('1mm')


class CurveCut(Simulation):

    def setup(self):
        self.cleanup()
        bevel = self.create_bevel_object()
        helper.move_object(bevel, self.internal_collection)
        self.obj.data.bevel_object = bevel

        self.obj.display_type = 'WIRE'
        modifier_name = constant.prefix + 'Solidify'
        self.obj.modifiers.new(modifier_name, 'SOLIDIFY')

    def update(self):
        bevel = helper.get_object_safely(f'{constant.prefix}{self.obj.name}.bevel')
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)

        mesh_obj = self.update_mesh()
        collection = self.obj.users_collection[0]
        sim_helper.adjust_boolean_modifiers(self.context, collection, mesh_obj)

    def create_bevel_object(self):
        name = f'{constant.prefix}{self.obj.name}.bevel'

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
        mesh_name = constant.prefix + self.obj.name + '.mesh'
        helper.delete_object(mesh_name)
        internal_collection = sim_helper.get_internal_collection(constant.prefix + 'internal', self.obj)

        # create a MESH version of the curve object
        depsgraph = self.context.evaluated_depsgraph_get()
        object_evaluated = self.obj.evaluated_get(depsgraph)
        mesh = bpy.data.meshes.new_from_object(object_evaluated)
        mesh_obj = bpy.data.objects.new(mesh_name, mesh)
        mesh_obj.matrix_world = self.obj.matrix_world
        sim_helper.cleanup_meshes(self.obj, mesh_name)
        self.obj.users_collection[0].objects.link(mesh_obj)
        helper.move_object(mesh_obj, internal_collection)
        helper.shade_mesh_flat(mesh_obj)
        helper.repair_mesh(self.context, mesh_obj)

        return mesh_obj


class MeshCut(Simulation):

    def setup(self):
        self.cleanup()
        self.obj.display_type = 'WIRE'
        self.obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')

        collection = self.obj.users_collection[0]

        sim_helper.adjust_boolean_modifiers(self.context, collection, self.obj)

    def update(self):

        cut_type = self.obj.soc_cut_type

        if cut_type == 'Cutout':

            perimeter_thickness = sim_helper.perimeter_thickness(self.obj)
            if perimeter_thickness:
                cutout_depth =  perimeter_thickness + helper.length('1mm')
            else:
                cutout_depth = helper.length('1cm')

            if self.obj.soc_cut_depth != cutout_depth:
                self.obj.soc_cut_depth = cutout_depth
            delta = 0.0
        elif cut_type == 'Pocket':
            delta = helper.length('0.1mm')
        else:
            delta = 0.0

        self.adjust_solidify_thickness(delta=delta)
