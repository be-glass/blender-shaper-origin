from bpy.props import FloatProperty, EnumProperty

cut_depth = FloatProperty(
    name="Cut Depth",
    description="Cut depth (mm)",
    default=0.0,
    min=-10.0,
    max=50.0,
    unit='LENGTH',
    options={'HIDDEN'},
)
tool_diameter = FloatProperty(
    name="Tool Diameter",
    description="Tool diameter (mm)",
    default=3.0,
    min=0.1,
    max=25.0,
    unit='LENGTH',
    options={'HIDDEN'},
)
reference_frame = EnumProperty(
    name="Reference",
    description="Reference",
    items=[('lcl', "Local", "local Reference", "", 0),
           ('glb', "Global", "global Reference", "", 1),
           ('obj', "Object", "relative to object", "", 2),
           ],
    default='lcl',
    options={'HIDDEN'},
)
cut_type = EnumProperty(
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
