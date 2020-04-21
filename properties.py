import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup

from . import handler


# Initialization


def register():
    bpy.utils.register_class(SceneProperties)

    bpy.types.Scene.so_cut = PointerProperty(type=SceneProperties)

    bpy.types.Object.soc_cut_depth = ObjectProperties.cut_depth
    bpy.types.Object.soc_tool_diameter = ObjectProperties.tool_diameter
    bpy.types.Object.soc_reference_frame = ObjectProperties.reference_frame
    bpy.types.Object.soc_mesh_cut_type = ObjectProperties.mesh_cut_type
    bpy.types.Object.soc_curve_cut_type = ObjectProperties.curve_cut_type
    bpy.types.Object.soc_object_type = ObjectProperties.object_type
    bpy.types.Object.soc_simulate = ObjectProperties.simulate
    bpy.types.Object.soc_initialized = ObjectProperties.initialized
    bpy.types.Object.soc_dogbone = ObjectProperties.dogbone
    bpy.types.Object.soc_solid_name = ObjectProperties.solid_name
    bpy.types.Object.soc_reference_name = ObjectProperties.reference_name
    bpy.types.Object.soc_preview_name = ObjectProperties.preview_name
    bpy.types.Object.soc_bevel_name = ObjectProperties.bevel_name
    bpy.types.Object.soc_known_as = ObjectProperties.known_as


def unregister():
    bpy.utils.unregister_class(SceneProperties)

    del bpy.types.Object.soc_cut_depth
    del bpy.types.Object.soc_tool_diameter
    del bpy.types.Object.soc_reference_frame
    del bpy.types.Object.soc_mesh_cut_type
    del bpy.types.Object.soc_curve_cut_type
    del bpy.types.Object.soc_object_type
    del bpy.types.Object.soc_simulate
    del bpy.types.Object.soc_initialized
    del bpy.types.Object.soc_dogbone
    del bpy.types.Object.soc_solid_name
    del bpy.types.Object.soc_reference_name
    del bpy.types.Object.soc_preview_name
    del bpy.types.Object.soc_bevel_name
    del bpy.types.Object.soc_known_as




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


# def preview(args):
#     pass


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
