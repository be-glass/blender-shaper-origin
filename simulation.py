import bpy

from . import constant, helper, sim_helper


def rebuild(context):
    active_obj = context.object
    cut_objs = sim_helper.find_cut_objects(context)
    bound_objs = [c.obj for c in context.scene.soc_cut_list]

    objects = ( set(cut_objs) - set(bound_objs) ) | set([active_obj])

    for obj in objects:
        create(context, obj)
    helper.select_active(context, active_obj)


def create(context, obj):

    helper.select_active(context, obj)

    sim_helper.delete_old_cuts(context, obj)

    if not obj.soc_simulate:
        return

    if obj.soc_cut_type == 'Perimeter':
        Perimeter(context, obj)

    elif obj.soc_cut_type in ['Exterior', 'Interior', 'Online']:
        if obj.type != 'CURVE':
            helper.error_msg("only curves here")
            return()

        CurveCut(context, obj)

    elif obj.soc_cut_type in ['Cutout', 'Pocket']:
        if obj.type != 'MESH':
            helper.error_msg("only meshes here")
            return ()

        MeshCut(context, obj)

    elif obj.soc_cut_type == 'None':
        pass

    else:
        helper.err_implementation()




def update(context):
    obj = context.object
    cuts = context.scene.soc_cut_list

    [cut.update(context) for cut in cuts if cut.obj == obj]





class Simulation:

    def __init__(self, context=None, obj=None):
        self.obj = obj
        context.scene.soc_cut_list.append(self)
        obj.display_type = 'TEXTURED'
        self.delete_modifiers()
        self.delete_internal_objects()

        self.internal_collection = sim_helper.get_internal_collection(constant.prefix + 'internal', obj)

    def delete(self, context):
        if self in context.scene.soc_cut_list:
            context.scene.soc_cut_list.remove(self)
        self.delete_modifiers()
        self.delete_internal_objects()

    def delete_modifiers(self):
        for modifier in self.obj.modifiers:
            if modifier.name.startswith(constant.prefix):
                self.obj.modifiers.remove(modifier)

    def delete_internal_objects(self):
        name = f'SOC_{self.obj.name}.bevel'

        # delete old object
        collection = self.obj.users_collection[0]
        if 'SOC_internal' in collection.children.keys():
            internal_collection = collection.children['SOC_internal']
            [bpy.data.objects.remove(o, do_unlink=True) for o in internal_collection.objects if
             o.name.startswith("SOC_" + self.obj.name)]

    def adjust_solidify_thickness(self, delta=0.0):
        if 'SOC_Solidify' in self.obj.modifiers:
            self.obj.modifiers['SOC_Solidify'].thickness = self.obj.soc_cut_depth + delta

    def perimeters(self, context):
        collection = context.object.users_collection[0]
        all_perimeters = sim_helper.find_siblings_by_type(context.object, 'Perimeter')
        perimeter_objs = [o for o in all_perimeters if o in collection.objects.keys()]
        return [c for c in context.scene.soc_cut_list if isinstance(c, Perimeter)]

class Perimeter(Simulation):
    def __init__(self, context, obj):
        super().__init__(context, obj)
        # obj.users_collection[0].soc_perimeters.append(self)
        self.setup(context)


    def setup(self, context):
        self.obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')

        for cut in sim_helper.find_siblings_by_type(self.obj, ['Cutout', 'Pocket', 'Exterior', 'Interior', 'Online']):
            modifier_name = "SOC_Boolean." + cut.name
            boolean = self.obj.modifiers.new(modifier_name, 'BOOLEAN')
            boolean.operation = 'DIFFERENCE'

            if cut.soc_cut_type in ['Cutout', 'Pocket']:
                boolean.object = cut

            elif cut.soc_cut_type in ['Exterior', 'Interior', 'Online']:
                mesh_name = f'SOC_{cut.name}.mesh'
                boolean.object = helper.get_object_safely(mesh_name)
            else:
                helper.err_implementation()

        self.update(context)

    def update(self, context):
        self.adjust_solidify_thickness()

    def adjust_boolean_modifiers(self, target_obj):
        modifier_name = f'SOC_Boolean.{target_obj.name}'
        self.obj.modifiers[modifier_name].object = target_obj


class CurveCut(Simulation):
    def __init__(self, context, obj):
        super().__init__(context, obj)
        self.setup(context)

    def setup(self, context):
        bevel = self.create_bevel_object()
        helper.move_object(bevel, self.internal_collection)
        self.obj.data.bevel_object = bevel
        self.update_mesh(context)
        self.obj.data.bevel_object = None

        self.obj.display_type = 'WIRE'
        for perimeter in sim_helper.find_siblings_by_type(self.obj, ['Perimeter']):
            perimeter.setup_booleans(context)  # need to rebuild the boolean modifiers

        self.update(context)

    def update(self, context):
        bevel = helper.get_object_safely(f'SOC_{self.obj.name}.bevel')
        bevel.scale = (self.obj.soc_tool_diameter, self.obj.soc_cut_depth, 1)
        self.update_mesh(context, self.obj)

    def create_bevel_object(self):
        name = f'SOC_{self.obj.name}.bevel'

        # create new one
        bpy.ops.mesh.primitive_plane_add(size=1.0)
        bevel = bpy.context.active_object
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

    def update_mesh(self, context):
        mesh_name = constant.prefix + self.obj.name + '.mesh'
        helper.delete_object(mesh_name)

        internal_collection = sim_helper.get_internal_collection(constant.prefix + 'internal', self.obj)

        helper.select_active(context, self.obj)
        r = bpy.ops.object.convert(target='MESH', keep_original=True)
        bpy.ops.object.shade_flat()
        mesh = context.object
        mesh.name = mesh_name
        helper.move_object(mesh, internal_collection)
        helper.select_active(context, self.obj)

        for perimeter in self.perimeters():
            perimeter.adjust_boolean_modifiers(mesh)


class MeshCut(Simulation):
    def __init__(self, context, obj):
        super().__init__(context, obj)
        # context.object.users_collection[0].soc_mesh_cuts.append(self)
        obj.modifiers.new("SOC_Solidify", 'SOLIDIFY')
        self.setup(context)

    def setup(self, context):
        self.obj.display_type = 'WIRE'

        for perimeter in self.perimeters(context):
            perimeter.adjust_boolean_modifiers(self.obj)

        self.update(context)

    def update(self, context):

        cut_type = self.obj.soc_cut_type

        if cut_type == 'Cutout':
            self.obj.soc_cut_depth = sim_helper.perimeter_thickness(self.obj) + 1.0
            delta = 0.0
        elif cut_type == 'Pocket':
            delta = 0.1
        else:
            delta = 0.0  # TODO check units

        self.adjust_solidify_thickness(delta=delta)
