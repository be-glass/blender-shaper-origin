import bpy
from bpy.props import FloatProperty, BoolProperty, StringProperty, EnumProperty, PointerProperty
from bpy.types import PropertyGroup

from . import constant, helper

# https://github.com/zeffii/BlenderPythonRecipes/wiki/Properties


def register():
    bpy.utils.register_class(SceneProperties)

    bpy.types.Scene.so_cut = PointerProperty(type=SceneProperties)

    bpy.types.Object.cut_depth = ObjectProperties.cut_depth
    bpy.types.Object.tool_diameter = ObjectProperties.tool_diameter
    bpy.types.Object.reference_frame = ObjectProperties.reference_frame
    bpy.types.Object.cut_type = ObjectProperties.cut_type



def unregister():
    bpy.utils.unregister_class(SceneProperties)
    del bpy.types.Scene.so_cut

    del bpy.types.Object.cut_depth
    del bpy.types.Object.tool_diameter
    del bpy.types.Object.reference_frame
    del bpy.types.Object.cut_type


def update_cut_depth(self, context):
    pass

def update_tool_diameter(self, context):
    pass

def update_cut_type(self, context: bpy.types.Context):
    obj = context.active_object
    obj.data.materials.clear()
    if obj.cut_type != 'None':
        material = helper.get_material(obj.cut_type)
        obj.data.materials.append(material)

class ObjectProperties(PropertyGroup):


    cut_depth = FloatProperty(
        name="Cut Depth",
        description="Cut depth (mm)",
        default=0.0,
        min=-10.0,
        max=50.0,
        unit='LENGTH',
        options={'HIDDEN'},
        update = update_cut_depth
    )

    tool_diameter = FloatProperty(
        name="Tool Diameter",
        description="Tool diameter (mm)",
        default=3.0,
        min=0.1,
        max=25.0,
        unit='LENGTH',
        options={'HIDDEN'},
        update = update_tool_diameter
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

    cut_type = EnumProperty(
        name="Cut Type",
        description="SO cut type",
        items=[('None', 'None', 'No Cut', '', 0),
               ('Interior', 'Interior', 'Interior Cut', '', 1),
               ('Exterior', 'Exterior', 'Exterior Cut', '', 2),
               ('Online', 'On Line', 'On Line Cut', '', 3),
               ('Pocket', 'Pocketing', 'Pocketing', '', 4),
               ('Guide', 'Guide', '', 'Guide Line', 5)],
        default='None',
        options = {'HIDDEN'},
        update = update_cut_type
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


