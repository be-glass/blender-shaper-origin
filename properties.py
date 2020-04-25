import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup

from . import handler


# Initialization


def register():
    bpy.utils.register_class(SceneProperties)

    bpy.types.Scene.so_cut = PointerProperty(type=SceneProperties)

    btO = bpy.types.Object
    oP = ObjectProperties

    btO.soc_cut_depth = oP.cut_depth
    btO.soc_tool_diameter = oP.tool_diameter
    btO.soc_reference_frame = oP.reference_frame
    btO.soc_mesh_cut_type = oP.mesh_cut_type
    btO.soc_curve_cut_type = oP.curve_cut_type
    btO.soc_object_type = oP.object_type
    btO.soc_simulate = oP.simulate
    btO.soc_initialized = oP.initialized
    btO.soc_dogbone = oP.dogbone
    btO.soc_solid_name = oP.solid_name
    btO.soc_reference_name = oP.reference_name
    btO.soc_preview_name = oP.preview_name
    btO.soc_bevel_name = oP.bevel_name
    btO.soc_known_as = oP.known_as


def unregister():
    bpy.utils.unregister_class(SceneProperties)
    btO = bpy.types.Object

    del btO.soc_cut_depth
    del btO.soc_tool_diameter
    del btO.soc_reference_frame
    del btO.soc_mesh_cut_type
    del btO.soc_curve_cut_type
    del btO.soc_object_type
    del btO.soc_simulate
    del btO.soc_initialized
    del btO.soc_dogbone
    del btO.soc_solid_name
    del btO.soc_reference_name
    del btO.soc_preview_name
    del btO.soc_bevel_name
    del btO.soc_known_as


# Definition

class ObjectProperties(PropertyGroup):
    cut_depth = FloatProperty(
        name="Cut Depth",
        description="Cut depth (mm)",
        default=0,
        min=0,
        max=float('inf'),
        unit='LENGTH',
        update=handler.update_cut_depth
    )

    tool_diameter = FloatProperty(
        name="Tool Diameter",
        description="Tool diameter (mm)",
        default=0,
        min=0,
        max=float('inf'),
        unit='LENGTH',
        update=handler.update_tool_diameter
    )

    reference_frame = EnumProperty(
        name="Reference",
        description="Reference",
        items=[('global', "Global", "global Reference", "", 0),
               ('local', "Local", "local Reference", "", 1),
               ],
        default='global',
        options={'HIDDEN'},
    )

    curve_cut_type = EnumProperty(
        name="Cut Type",
        description="SO cut type",
        items=[('None', 'None', 'No Cut', '', 0),
               ('Exterior', 'Exterior', 'Exterior Cut', '', 2),
               ('Interior', 'Interior', 'Interior Cut', '', 4),
               ('Online', 'On Line', 'On Line Cut', '', 6),
               ('GuidePath', 'Guide Path', '', 'Guide Line', 7),
               ],

        default='None',
        options={'HIDDEN'},
        update=handler.update_cut_type
    )
    mesh_cut_type = EnumProperty(
        name="Cut Type",
        description="SO cut type",
        items=[('None', 'None', 'No Cut', '', 0),
               ('Perimeter', 'Perimeter', "Defines the outer perimeter of work piece", 1),
               ('Cutout', 'Cutout', 'Cutout', 3),
               ('Pocket', 'Pocketing', 'Pocketing', '', 5),
               ('GuideArea', 'Guide Area', '', 'Guide Line', 7),
               ],

        default='None',
        options={'HIDDEN'},
        update=handler.update_cut_type
    )
    object_type = EnumProperty(
        name="Object Type",
        description="SO object type",
        items=[('None', 'None', 'None', '', 0),
               ('Cut', 'Cut', "Cut", 1),
               ('Preview', 'Preview', 'Preview', 2),
               ('Reference', 'Reference', 'Reference', '', 3),
               ('Bounding', 'Bounding', 'Bounding', '', 4),
               ('Helper', 'Helper', 'Helper', '', 5),
               ('Proxy', 'Proxy', 'Proxy', '', 6),
               ],

        default='None',
        options={'HIDDEN'},
    )
    simulate = BoolProperty(
        name="Simulate cut",
        description="Simulate cut",
        default=True,
        options={'HIDDEN'},
        update=handler.update_cut_type
    )
    initialized = BoolProperty(
        name="Object initialized",
        description="Object is initialized (for internal use)",
        default=False,
        options={'HIDDEN'},
    )
    dogbone = BoolProperty(
        name="Dogbone Fillets",
        description="Add dogbone fillets to cut",
        default=False,
        options={'HIDDEN'},
        update=handler.update_cut_type
    )
    solid_name = StringProperty(
        name="Solid Mesh Name",
        description="Internal record of solid name",
        default="",
    )
    preview_name = StringProperty(
        name="Preview Object Name",
        description="Internal record of preview object name",
        default="",
    )
    reference_name = StringProperty(
        name="Reference Name",
        description="Internal record of reference object name",
        default="",
    )
    bevel_name = StringProperty(
        name="Bevel Name",
        description="Internal record of bevel helper object name",
        default="",
    )
    known_as = StringProperty(
        name="Known as",
        description="Internal record of object association",
        default="",
    )


class SceneProperties(PropertyGroup):
    use_transformations: BoolProperty(
        name="Apply transformations",
        description="Apply object transformations during export",
        default=True,
        options={'HIDDEN'},
    )
    selected_only: BoolProperty(
        name="Selected Only",
        description="Export only selected objects",
        default=False,
        options={'HIDDEN'},
    )
    separate_files: BoolProperty(
        name="Separate Files",
        description="Export each shape in a separate file",
        default=False,
        options={'HIDDEN'},
    )
    preview: BoolProperty(
        name="Preview",
        description="Preview export in X-Y-plane",
        default=False,
        options={'HIDDEN'},
        update=handler.preview
    )
    export_path: StringProperty(
        name="Export Directory",
        description="Path to directory where the files are created",
        default="//",
        maxlen=1024,
        subtype="DIR_PATH",
        options={'HIDDEN'},
    )
