from .shape.curveguide import CurveGuide
from .shape.proxy import Proxy
from ..constant import PREFIX
from ..fillet import Fillet
from ..helper.gen_helper import find_perimeters, boolean_modifier_name, delete_modifier
from ..helper.other import get_object_safely, err_implementation, get_solid_collection

from .shape.curve import CurveCut
from .shape.mesh import MeshCut
from .shape.meshguide import MeshGuide
from .shape.perimeter import Perimeter


class Simulation:

    def __init__(self, context, cut_obj):
        self.collection = get_solid_collection(self.context)
        self.context = context
        self.cut_obj = cut_obj
        self.obj = None

    def update(self):
        pass

    def setup(self):
        self.shape = self.shape_factory()
        self.solid = self.solid_factory()

    def cleanup(self):
        pass

    def shape_factory(self):
        if self.cut_obj.soc_mesh_cut_type == 'Perimeter':
            shape = Perimeter
        elif self.cut_obj.soc_curve_cut_type in ['Exterior', 'Interior', 'Online'] and self.cut_obj.type == 'CURVE':
            shape = CurveCut
        elif self.cut_obj.soc_mesh_cut_type in ['Cutout', 'Pocket'] and self.cut_obj.type == 'MESH':
            shape = MeshCut
        elif self.cut_obj.soc_mesh_cut_type == 'GuideArea':
            shape = MeshGuide
        elif self.cut_obj.soc_mesh_cut_type == 'GuidePath':
            shape = CurveGuide
        else:
            err_implementation(self.context)
            return None
        return shape(self.context, self.cut_obj)

    def solid_factory(self):
        if self.cut_obj.soc_mesh_cut_type:
            solid = Fillet
        elif self.cut_obj.soc_curve_cut_type:
            solid = Proxy
        else:
            err_implementation(self.context)
            return None
        return solid(self.context, self.cut_obj)


--


def adjust_solidify_thickness(self, delta=0.0):
    master = self.obj
    revision = self.get_fillet_obj()

    modifier_name = PREFIX + 'Solidify'
    if modifier_name in revision.modifiers:
        revision.modifiers[modifier_name].thickness = master.soc_cut_depth + delta


def adjust_boolean_modifiers(self, collection):
    for perimeter_obj in find_perimeters(collection):
        self.rebuild_boolean_modifier(perimeter_obj, self.obj)


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
