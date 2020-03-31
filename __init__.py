import bpy
from bpy import utils
from bpy.props import PointerProperty


bl_info = {
    "name": "SO Cutting Toolbox",
    "author": "Boris Glass 8)",
    "blender": (2, 82, 0),
    "version": (0, 0, 2),
    "location": "3D View > Sidebar",
    "description": "SVG Export Utilities for cutting lines",
    # "wiki_url": "https://docs.blender.org/manual/en/dev/addons/mesh/3d_print_toolbox.html",
    # "support": 'OFFICIAL',
    "category": "Mesh",
}

from . import ui, properties



# why does it only work without the registrations???
widgets = (
    # properties.SceneProperties,
     # ui.BG_PT_SOC_select,
     # ui.BG_PT_SOC_init,
     # ui.BG_PT_SOC_export,
)

def register():
    for widget in widgets:
        utils.register_class(widget)

    bpy.types.Scene.so_cut = PointerProperty(type=properties.SceneProperties)


def unregister():
    for widget in widgets:
        utils.unregister_class(widget)

    del bpy.types.Scene.so_cut
