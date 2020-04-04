





from . import ui, properties, operators

# https://wiki.blender.org/wiki/Process/Addons/Guidelines/metainfo

bl_info = {
    "name": "SO Cutting Toolbox",
    "author": "Boris Glass 8)",
    "blender": (2, 80, 0),
    "version": (0, 0, 3),
    "location": "3D View > Sidebar",
    "description": "SVG Export Utilities for cutting lines",
    # "wiki_url": "https://docs.blender.org/manual/en/dev/addons/mesh/3d_print_toolbox.html",
    # "support": 'OFFICIAL',
    "category": "Mesh",
}

files = [ui, properties, operators]

operators.bl_info = bl_info


def register():
    [file.register() for file in files]


def unregister():
    [file.unregister() for file in files]

