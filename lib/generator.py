from .generators.bounding import Bounding
from .generators.curve_cut import CurveCut
from .generators.disabled import Disabled
from .generators.gen_preview import PreviewPerimeter
from .generators.mesh_cut import MeshCut
from .generators.perimeter import Perimeter
from .generators.proxy import Proxy
from .generators.ignore import Ignore
from .helper.other import err_implementation


def create_cut(context, obj):
    ot = obj.soc_object_type

    if not obj.soc_simulate:
        cut = Disabled

    elif ot in ['None', 'Cut']:
        if obj.soc_mesh_cut_type == 'Perimeter':
            cut = Perimeter
        elif obj.soc_curve_cut_type in ['Exterior', 'Interior', 'Online'] and obj.type == 'CURVE':
            cut = CurveCut
        elif obj.soc_mesh_cut_type in ['Cutout', 'Pocket'] and obj.type == 'MESH':
            cut = MeshCut
        else:
            cut = Disabled

    elif ot == 'Preview':
        if obj.soc_mesh_cut_type == 'Perimeter':
            cut = PreviewPerimeter
        elif obj.soc_mesh_cut_type != 'None':
            cut = Ignore
        elif obj.soc_curve_cut_type != 'None':
            cut = Ignore
        else:
            err_implementation(context)
            cut = Ignore

    elif ot == 'Bounding':
        cut = Bounding

    elif ot == 'Solid':
        cut = Ignore

    elif ot == 'Proxy':
        cut = Proxy
    else:
        cut = Disabled
    return cut(context, obj)
