import bpy
from bpy import utils
from bpy.props import PointerProperty


bl_info = {
    "name": "SO Cutting Toolbox",
    "author": "Boris Glass 8)",
    "blender": (2, 82, 0),
    "version": (0, 0, 3),
    "location": "3D View > Sidebar",
    "description": "SVG Export Utilities for cutting lines",
    # "wiki_url": "https://docs.blender.org/manual/en/dev/addons/mesh/3d_print_toolbox.html",
    # "support": 'OFFICIAL',
    "category": "Mesh",
}

from . import ui, properties


def register():
    ui.register()

    # bpy.types.Scene.so_cut = PointerProperty(type=properties.SceneProperties)



    properties.register()

def unregister():
    ui.unregister()
    properties.unregister()

