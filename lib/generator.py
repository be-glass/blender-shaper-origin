from .generators.bounding import Bounding
from .generators.curve_cut import CurveCut
from .generators.disabled import Disabled
from .generators.gen_preview import *
from .generators.mesh_cut import MeshCut
from .generators.perimeter import Perimeter
from .generators.proxy import Proxy
from .helper.other import err_implementation


def create_cut(self, obj):
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

    elif ot == 'Preview':
        if self.obj.soc_mesh_cut_type == 'Perimeter':
            cut == PreviewPerimeter
        elif self.obj.soc_mesh_cut_type != 'None':
            cut = MeshCut
        elif self.obj.soc_curve_cut_type != 'None':
            cut = CurveCut
        else:
            err_implementation(self.context)

    elif ot == 'Bounding':
        cut == Bounding


    elif ot == 'Proxy':
        cut = Proxy
    else:
        cut = Disabled
    return cut(self.context, self.obj)
