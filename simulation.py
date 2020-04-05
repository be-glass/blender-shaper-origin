import bpy

from . import constant, helper, sim_helper


def update(context, reset=False):
    obj = context.object

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
    helper.select_active(context, obj)


class Simulation:

    def __init__(self, context, obj):
        self.obj = obj
        self.context = context
        self.internal_collection = sim_helper.get_internal_collection(constant.prefix + 'internal', obj)

    def cleanup(self):
        sim_helper.delete_modifiers(self.obj)
        sim_helper.delete_internal_objects(self.obj)

    def adjust_solidify_thickness(self, delta=0.0):
        if 'SOC_Solidify' in self.obj.modifiers:
            self.obj.modifiers['SOC_Solidify'].thickness = self.obj.soc_cut_depth + delta


class Perimeter(Simulation):

    def setup(self):
        self.cleanup()
        self.obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')

        for cut in sim_helper.find_siblings_by_type(self.obj, ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']):
            sim_helper.rebuild_boolean_modifier(self, cut)

    def update(self):
        self.adjust_solidify_thickness()

        cutouts = sim_helper.find_siblings_by_type(self.context.object, 'Cutout')
        for cut in cutouts:
            cut_sim = MeshCut(self.context, cut)
            cut_sim.update()

class CurveCut(Simulation):

    def setup(self):
        self.cleanup()
        bevel = self.create_bevel_object()
        helper.move_object(bevel, self.internal_collection)
        self.obj.data.bevel_object = bevel
        self.update_mesh()
        self.obj.data.bevel_object = None

        self.obj.display_type = 'WIRE'
        for perimeter in sim_helper.find_siblings_by_type(self.obj, ['Perimeter']):
            perimeter.setup_booleans(self.context)

    def update(self):
        bevel = helper.get_object_safely(f'SOC_{self.obj.name}.bevel')
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)
        self.update_mesh()

    def create_bevel_object(self):
        name = f'SOC_{self.obj.name}.bevel'

        # create new one
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        bevel = self.context.active_object
        bevel.name = name

        # move object origin to upper edge
        bevel.location = (0, -0.5, 0)
        bpy.ops.object.transform_apply()

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

        helper.select_active(self.context, self.obj)
        bpy.ops.object.convert(target='MESH', keep_original=True)
        bpy.ops.object.shade_flat()
        mesh = self.context.object
        mesh.name = mesh_name
        helper.move_object(mesh, internal_collection)
        helper.select_active(self.context, self.obj)

        sim_helper.adjust_boolean_modifiers(self.context, mesh)


class MeshCut(Simulation):

    def setup(self):
        self.cleanup()
        self.obj.display_type = 'WIRE'
        self.obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')

        sim_helper.adjust_boolean_modifiers(self.context, self.obj)

    def update(self):

        cut_type = self.obj.soc_cut_type

        if cut_type == 'Cutout':
            self.obj.soc_cut_depth = sim_helper.perimeter_thickness(self.obj) + 1.0
            delta = 0.0
        elif cut_type == 'Pocket':
            delta = 0.1
        else:
            delta = 0.0  # TODO check units

        self.adjust_solidify_thickness(delta=delta)
