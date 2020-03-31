import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty, IntProperty
from bpy.types import PropertyGroup
from . import props

# https://github.com/zeffii/BlenderPythonRecipes/wiki/Properties


def register():
    bpy.utils.register_class(SceneProperties)

    bpy.types.Scene.so_cut = PointerProperty(type=SceneProperties)

    bpy.types.Object.cut_depth = props.cut_depth
    bpy.types.Object.tool_diameter = props.tool_diameter
    bpy.types.Object.reference_frame = props.reference_frame
    bpy.types.Object.cut_type = props.cut_type

def unregister():
    bpy.utils.unregister_class(SceneProperties)
    del bpy.types.Scene.so_cut

    del bpy.types.Object.cut_depth
    del bpy.types.Object.tool_diameter
    del bpy.types.Object.reference_frame
    del bpy.types.Object.cut_type


class SceneProperties(PropertyGroup):

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


