import bpy
from bpy import utils
from bpy.types import Panel

from . import gen_helper


def panels():
    return [
        BG_PT_SOC_export,
        # BG_PT_SOC_init,
        BG_PT_SOC_select,
    ]


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


class BG_PT_SOC_export(SOCutPanel, Panel):
    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True
        soc = context.scene.so_cut

        # Widgets
        layout.prop(soc, "preview")
        layout.prop(soc, "selected_only")
        layout.prop(soc, "use_transformations")
        layout.prop(soc, "export_path")
        layout.prop(soc, "separate_files")
        layout.operator("mesh.socut_export_cuts", text="Export Cuts")


class BG_PT_SOC_select(SOCutPanel, Panel):
    bl_label = "Item Settings"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = True

        obj = bpy.context.active_object

        if obj:
            typ = obj.soc_object_type

            if typ == 'None':
                self.draw_type_select(obj)

            elif typ == 'Cut':
                self.draw_cut(obj)

            elif typ == 'Bounding':
                self.layout.label(text="Bounding Frame")

            elif typ == 'Preview':
                self.layout.label(text="Preview Item")

            elif typ == 'Reference':
                self.layout.label(text="Reference Item")

    def draw_cut(self, obj):
        layout = self.layout

        self.draw_type_select(obj)

        if obj.soc_mesh_cut_type != 'None' or obj.soc_curve_cut_type != 'None':
            layout.prop(obj, "soc_reference_frame")
            layout.prop(obj, "soc_cut_depth")
            layout.prop(obj, "soc_tool_diameter")
            layout.prop(obj, "soc_simulate")
            layout.prop(obj, "soc_dogbone")

        collection = obj.users_collection[0]
        perimeters = gen_helper.find_perimeters(collection)
        if obj.soc_mesh_cut_type != 'Perimeter' and len(perimeters) > 0:
            layout.operator("mesh.socut_align_object")

    def draw_type_select(self, obj):
        if obj.type == 'MESH':
            self.layout.prop(obj, "soc_mesh_cut_type")
        elif obj.type == 'CURVE':
            self.layout.prop(obj, "soc_curve_cut_type")
