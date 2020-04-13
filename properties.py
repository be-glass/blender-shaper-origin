import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup

from . import fillet, generator
from .constant import defaults
from .helper import length
from .sim_helper import cleanup


# Initialization


def register():
    bpy.utils.register_class(SceneProperties)

    bpy.types.Scene.so_cut = PointerProperty(type=SceneProperties)

    bpy.types.Object.soc_cut_depth = ObjectProperties.cut_depth
    bpy.types.Object.soc_tool_diameter = ObjectProperties.tool_diameter
    bpy.types.Object.soc_reference_frame = ObjectProperties.reference_frame
    bpy.types.Object.soc_mesh_cut_type = ObjectProperties.mesh_cut_type
    bpy.types.Object.soc_curve_cut_type = ObjectProperties.curve_cut_type
    bpy.types.Object.soc_simulate = ObjectProperties.simulate
    bpy.types.Object.soc_initialized = ObjectProperties.initialized
    bpy.types.Object.soc_dogbone = ObjectProperties.dogbone


def unregister():
    bpy.utils.unregister_class(SceneProperties)

    del bpy.types.Object.soc_cut_depth
    del bpy.types.Object.soc_tool_diameter
    del bpy.types.Object.soc_reference_frame
    del bpy.types.Object.soc_mesh_cut_type
    del bpy.types.Object.soc_curve_cut_type
    del bpy.types.Object.soc_simulate
    del bpy.types.Object.soc_initialized
    del bpy.types.Object.soc_dogbone


# Update

def minmax(context, property_name):
    d0, dd, d1 = defaults[property_name]
    return length(context, d0), \
           length(context, d1)


def default(context, property_name):
    d0, dd, d1 = defaults[property_name]
    return length(context, dd)


def update_cut_depth(obj, context):
    minimum, maximum = minmax(context, 'cut_depth')

    if obj.soc_initialized:
        if obj.soc_cut_depth < minimum:
            obj.soc_cut_depth = minimum
        elif obj.soc_cut_depth > maximum:
            obj.soc_cut_depth = maximum
        else:
            generator.update(context, obj)


def update_tool_diameter(obj, context):
    minimum, maximum = minmax(context, 'tool_diameter')

    if obj.soc_initialized:
        if obj.soc_tool_diameter < minimum:
            obj.soc_tool_diameter = minimum
        elif obj.soc_tool_diameter > maximum:
            obj.soc_tool_diameter = maximum
        else:
            generator.update(context, obj)

def initialize_object(obj, context):
    obj.soc_cut_depth = default(context, 'cut_depth')
    obj.soc_tool_diameter = default(context, 'tool_diameter')
    obj.soc_initialized = True


def update_cut_type(obj, context):
    if not obj.soc_initialized:
        initialize_object(obj, context)
    generator.update(context, obj)


# Definition

class ObjectProperties(PropertyGroup):
    cut_depth = FloatProperty(
        name="Cut Depth",
        description="Cut depth (mm)",
        default=0,
        min=0,
        max=float('inf'),
        unit='LENGTH',
        update=update_cut_depth
    )

    tool_diameter = FloatProperty(
        name="Tool Diameter",
        description="Tool diameter (mm)",
        default=0,
        min=0,
        max=float('inf'),
        unit='LENGTH',
        update=update_tool_diameter
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
        update=update_cut_type
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
        update=update_cut_type
    )
    simulate = BoolProperty(
        name="Simulate cut",
        description="Simulate cut",
        default=True,
        options={'HIDDEN'},
        update=update_cut_type
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
        update=update_cut_type
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
    export_path: StringProperty(
        name="Export Directory",
        description="Path to directory where the files are created",
        default="//",
        maxlen=1024,
        subtype="DIR_PATH",
        options={'HIDDEN'},
    )
