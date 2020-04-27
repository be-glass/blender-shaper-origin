#  This file is part of Blender_Shaper_Origin.
#
#  Blender_Shaper_Origin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Blender_Shaper_Origin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Blender_Shaper_Origin.  If not, see <https://www.gnu.org/licenses/>.

import bpy
from bpy import utils
from bpy.types import Panel

from .lib.helper import gen_helper


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


class BG_PT_SOC_export(Panel):
    bl_category = "SO Cut"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bl_label = "Export"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True
        soc = context.scene.so_cut

        # Widgets
        layout.prop(soc, "preview")
        layout.prop(soc, "selected_only")
        layout.prop(soc, "export_path")
        layout.prop(soc, "separate_files")
        layout.operator("mesh.socut_rebuild", text="Rebuild")
        layout.operator("mesh.socut_export_cuts", text="Export Cuts")


class BG_PT_SOC_select(Panel):
    bl_category = "Item"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    bl_label = "SO Cut Settings"

    def draw(self, context):
        self.layout.use_property_split = True
        self.layout.use_property_decorate = True

        obj = bpy.context.active_object

        if obj:
            typ = obj.soc_object_type

            if typ == 'None':
                self.draw_type_select(obj)
                self.draw_align_with_perimeter(obj)

            elif typ == 'Cut':
                self.draw_cut(obj)
                self.draw_align_with_perimeter(obj)

            elif typ == 'Bounding':
                self.layout.label(text="Bounding Frame")

            elif typ == 'Preview':
                self.layout.label(text="Preview Item")

            elif typ == 'Reference':
                self.layout.label(text="Reference Item")

            elif typ == 'Helper':
                self.layout.label(text="Helper Item")

    def draw_cut(self, obj):
        layout = self.layout

        self.draw_type_select(obj)

        if obj.soc_mesh_cut_type != 'None' or obj.soc_curve_cut_type != 'None':
            layout.prop(obj, "soc_cut_depth")
            layout.prop(obj, "soc_tool_diameter")
            layout.prop(obj, "soc_simulate")
            layout.prop(obj, "soc_dogbone")

    def draw_align_with_perimeter(self, obj):
        collection = obj.users_collection[0]
        perimeters = gen_helper.find_perimeters(collection)
        if obj.soc_mesh_cut_type != 'Perimeter' and len(perimeters) > 0:
            self.layout.operator("mesh.socut_align_object")

    def draw_type_select(self, obj):
        if obj.type == 'MESH':
            self.layout.prop(obj, "soc_mesh_cut_type")
        elif obj.type == 'CURVE':
            self.layout.prop(obj, "soc_curve_cut_type")
