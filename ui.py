from bpy.types import Panel


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

        layout.label(text="Scale To")
        row = layout.row(align=True)
        # layout.row.operator("mesh.print3d_scale_to_volume", text="Export Cuts")

