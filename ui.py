from bpy import utils
from bpy.types import Panel


def panels():
    return (
     BG_PT_SOC_init,
     BG_PT_SOC_select,
     BG_PT_SOC_export,
    )

def register():
    for widget in panels():
        utils.register_class(widget)


def unregister():
    for widget in panels():
        utils.unregister_class(widget)


class SOCutPanel:
    bl_category = "SO Cut"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'


class BG_PT_SOC_select(SOCutPanel, Panel):
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True
        soc = context.scene.so_cut

        # Widgets
        layout.prop(soc, "cut_type")
        layout.prop(soc, "reference_frame")
        layout.prop(soc, "cut_depth")
        layout.prop(soc, "tool_diameter")


class BG_PT_SOC_init(SOCutPanel, Panel):
    bl_label = "Initialization"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True
        soc = context.scene.so_cut

        # Widgets
        layout.operator("mesh.socut_create_materials", text="Create Materials")
        layout.operator("mesh.socut_create_sheet", text="Create Sheet")


class BG_PT_SOC_export(SOCutPanel, Panel):
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True
        soc = context.scene.so_cut

        # Widgets
        layout.prop(soc, "selected_only")
        layout.prop(soc, "use_apply_scale")
        layout.prop(soc, "export_path")

        layout.operator("mesh.socut_export_cuts", text="Export Cuts")

