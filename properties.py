import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup


def register():
    bpy.utils.register_class(SceneProperties)
    bpy.types.Scene.so_cut = PointerProperty(type=SceneProperties)


def unregister():
    bpy.utils.unregister_class(SceneProperties)
    del bpy.types.Scene.so_cut


class SceneProperties(PropertyGroup):

    cut_depth: FloatProperty(
        name="Cut Depth",
        description="Cut depth (mm)",
        default=0.0,
        min=-10.0,
        max=50.0,
        unit='LENGTH',
        options={'HIDDEN'},
    )
    tool_diameter: FloatProperty(
        name="Tool Diameter",
        description="Tool diameter (mm)",
        default=3.0,
        min=0.1,
        max=25.0,
        unit='LENGTH',
        options={'HIDDEN'},
    )
    use_apply_scale: BoolProperty(
        name="Apply Scale",
        description="Apply scene scale setting on export",
        default=False,
        options={'HIDDEN'},
    )
    selected_only: BoolProperty(
        name="Selected Only",
        description="Export only selected objects",
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
    reference_frame: EnumProperty(
        name="Reference",
        description="Reference",
        items=[('lcl', "Local", "local Reference", "", 0),
               ('glb', "Global", "global Reference", "", 1),
               ('obj', "Object", "relative to object", "", 2),
               ],
        default='lcl',
        options={'HIDDEN'},
    )
    cut_type : EnumProperty(
        name="Cut Type",
        description="SO cut type",
        items=[('int', 'Interior', 'Interior Cut', '', 0),
               ('ext', 'Exterior', 'Exterior Cut', '',1),
               ('onl,', 'On Line', 'On Line Cut', '',2),
               ('pck', 'Pocketing', 'Pocketing', '',3),
               ('gid', 'Guide', '', 'Guide Line',4)],
        default='int',
        options={'HIDDEN'},
    )


